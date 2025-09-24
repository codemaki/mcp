#!/usr/bin/env python3
"""MCP Server for SKB content search"""

import asyncio
import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
import uvicorn
from bs4 import BeautifulSoup
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("mcp-skb-search")

# HTTP client for making requests
client = httpx.AsyncClient()

@mcp.tool()
async def search_content_autocomplete(search_keyword: str) -> str:
    """
    Search for content using autocomplete to get a list of available titles.
    This is step 1 - helps users find the exact content title they want.

    Args:
        search_keyword: The search term to find content (e.g., "백설공주")

    Returns:
        JSON string with search results containing titles and indices
    """
    url = "https://www.bworld.co.kr/myb/btv/link/search/autoComplete.do"

    try:
        response = await client.post(
            url,
            json={"searchKeyword": search_keyword},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        data = response.json()

        if data.get("code") != "00" or data.get("result", {}).get("result") != "0000":
            return json.dumps({
                "error": "Search failed",
                "message": "API returned error code"
            })

        results = data.get("result", {}).get("results", [])

        if not results:
            return json.dumps({
                "message": f"No results found for '{search_keyword}'",
                "results": []
            })

        formatted_results = []
        for item in results:
            formatted_results.append({
                "idx": item.get("idx"),
                "title": item.get("title")
            })

        return json.dumps({
            "search_keyword": search_keyword,
            "total_results": data.get("result", {}).get("total_result_no", 0),
            "results": formatted_results
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": "Request failed",
            "message": str(e)
        })


@mcp.tool()
async def search_content_episodes(search_term: str) -> str:
    """
    Search for content to get all related episode IDs.
    This is step 2 - gets all episode IDs that match the search term.
    Note: This returns multiple episodes that contain or are related to the search term.

    Args:
        search_term: The search term to find related content

    Returns:
        JSON string with all episode IDs found for the search term
    """
    # URL encode the search keyword
    encoded_keyword = quote(search_term)
    url = f"https://www.bworld.co.kr/myb/btv/link/pages/vodSearchResult.do?searchKeyword={encoded_keyword}"

    try:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <li> elements in the VOD results
        vod_items = soup.select('ul.thumbnail-list li a.badge-wrap')

        if not vod_items:
            return json.dumps({
                "message": f"No episodes found for '{search_term}'",
                "episode_ids": []
            })

        episode_ids = []
        for item in vod_items:
            episode_id = item.get('data-epsd-id')
            series_id = item.get('data-sris-id')

            # Get thumbnail image
            img_tag = item.find('img')
            thumbnail_url = img_tag.get('src') if img_tag else None

            if episode_id:
                episode_ids.append({
                    "episode_id": episode_id,
                    "series_id": series_id,
                    "thumbnail_url": thumbnail_url
                })

        return json.dumps({
            "search_term": search_term,
            "total_found": len(episode_ids),
            "episode_ids": episode_ids
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": "Request failed",
            "message": str(e)
        })


@mcp.tool()
async def get_episode_details(episode_id: str) -> str:
    """
    Get detailed information about a specific episode using its episode ID.
    This is step 3 - gets comprehensive details about the content.

    Args:
        episode_id: The episode ID (e.g., "CE1000386027")

    Returns:
        JSON string with detailed episode information including synopsis, cast, etc.
    """
    url = "https://www.bworld.co.kr/myb/btv/link/search/singleSynopsis.do"

    try:
        response = await client.post(
            url,
            json={"epsdId": episode_id},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        data = response.json()

        if data.get("code") != "00":
            return json.dumps({
                "error": "Request failed",
                "message": "API returned error code"
            })

        result = data.get("result", {})

        # Clean HTML from synopsis
        synopsis = result.get("epsdSnssCts", "")
        if synopsis:
            synopsis = re.sub(r'<br\s*/?>', '\n', synopsis)
            synopsis = re.sub(r'<[^>]*>', '', synopsis)

        episode_details = {
            "episode_id": episode_id,
            "title": result.get("title"),
            "title_image": result.get("titleImgPath"),
            "release_year": result.get("openYr"),
            "duration_minutes": result.get("playTmsVal"),
            "synopsis": synopsis.strip(),
            "director": result.get("director"),
            "actors": result.get("actor"),
            "series_choice_name": result.get("ssonChoicNm"),
            "broadcast_channel": result.get("brcastChnlNm"),
            "rating": {
                "btv_like_rate": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeRate"),
                "btv_like_count": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeNcnt")
            }
        }

        # Remove None values
        episode_details = {k: v for k, v in episode_details.items() if v is not None}

        return json.dumps(episode_details, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": "Request failed",
            "message": str(e)
        })


@mcp.tool()
async def find_exact_content(exact_title: str) -> str:
    """
    Find content with exact title match by searching episodes and checking their details.
    This combines steps 2 and 3 - searches for episodes and finds the one with matching title.

    Args:
        exact_title: The exact title to search for (e.g., "다이 하드", "다이 하드3")

    Returns:
        JSON string with detailed information of the content with matching title
    """
    try:
        # Step 1: Search for episodes using the same logic as search_content_episodes
        encoded_keyword = quote(exact_title)
        search_url = f"https://www.bworld.co.kr/myb/btv/link/pages/vodSearchResult.do?searchKeyword={encoded_keyword}"

        response = await client.get(search_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        vod_items = soup.select('ul.thumbnail-list li a.badge-wrap')

        if not vod_items:
            return json.dumps({
                "message": f"No episodes found for '{exact_title}'",
                "exact_match_found": False
            })

        # Step 2: Check each episode to find exact title match
        checked_episodes = []
        for item in vod_items:
            episode_id = item.get('data-epsd-id')
            if not episode_id:
                continue

            # Get episode details using the same logic as get_episode_details
            details_url = "https://www.bworld.co.kr/myb/btv/link/search/singleSynopsis.do"
            details_response = await client.post(
                details_url,
                json={"epsdId": episode_id},
                headers={"Content-Type": "application/json"}
            )
            details_response.raise_for_status()

            details_data = details_response.json()
            if details_data.get("code") != "00":
                continue

            result = details_data.get("result", {})
            episode_title = result.get("title", "")

            checked_episodes.append({
                "episode_id": episode_id,
                "title": episode_title
            })

            # Check for exact match (case-insensitive)
            if episode_title.lower().strip() == exact_title.lower().strip():
                # Clean HTML from synopsis
                synopsis = result.get("epsdSnssCts", "")
                if synopsis:
                    synopsis = re.sub(r'<br\s*/?>', '\n', synopsis)
                    synopsis = re.sub(r'<[^>]*>', '', synopsis)

                episode_details = {
                    "episode_id": episode_id,
                    "title": result.get("title"),
                    "title_image": result.get("titleImgPath"),
                    "release_year": result.get("openYr"),
                    "duration_minutes": result.get("playTmsVal"),
                    "synopsis": synopsis.strip(),
                    "director": result.get("director"),
                    "actors": result.get("actor"),
                    "series_choice_name": result.get("ssonChoicNm"),
                    "broadcast_channel": result.get("brcastChnlNm"),
                    "rating": {
                        "btv_like_rate": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeRate"),
                        "btv_like_count": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeNcnt")
                    }
                }

                # Remove None values
                episode_details = {k: v for k, v in episode_details.items() if v is not None}

                return json.dumps({
                    "exact_match_found": True,
                    "search_title": exact_title,
                    "matched_episode": episode_details
                }, ensure_ascii=False, indent=2)

        # If no exact match found, return the first episode as fallback
        if checked_episodes:
            first_episode_id = vod_items[0].get('data-epsd-id')
            if first_episode_id:
                # Get details for first episode
                details_url = "https://www.bworld.co.kr/myb/btv/link/search/singleSynopsis.do"
                details_response = await client.post(
                    details_url,
                    json={"epsdId": first_episode_id},
                    headers={"Content-Type": "application/json"}
                )
                details_response.raise_for_status()

                details_data = details_response.json()
                if details_data.get("code") == "00":
                    result = details_data.get("result", {})

                    # Clean HTML from synopsis
                    synopsis = result.get("epsdSnssCts", "")
                    if synopsis:
                        synopsis = re.sub(r'<br\s*/?>', '\n', synopsis)
                        synopsis = re.sub(r'<[^>]*>', '', synopsis)

                    fallback_details = {
                        "episode_id": first_episode_id,
                        "title": result.get("title"),
                        "title_image": result.get("titleImgPath"),
                        "release_year": result.get("openYr"),
                        "duration_minutes": result.get("playTmsVal"),
                        "synopsis": synopsis.strip(),
                        "director": result.get("director"),
                        "actors": result.get("actor"),
                        "series_choice_name": result.get("ssonChoicNm"),
                        "broadcast_channel": result.get("brcastChnlNm"),
                        "rating": {
                            "btv_like_rate": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeRate"),
                            "btv_like_count": result.get("review", {}).get("btvPntInfo", {}).get("btvLikeNcnt")
                        }
                    }

                    # Remove None values
                    fallback_details = {k: v for k, v in fallback_details.items() if v is not None}

                    return json.dumps({
                        "exact_match_found": False,
                        "search_title": exact_title,
                        "message": f"No exact match found for '{exact_title}'. Returning first result as fallback.",
                        "fallback_episode": fallback_details,
                        "total_episodes_checked": len(checked_episodes),
                        "checked_titles": [ep["title"] for ep in checked_episodes]
                    }, ensure_ascii=False, indent=2)

        return json.dumps({
            "exact_match_found": False,
            "search_title": exact_title,
            "message": "No episodes found to check for exact match"
        })

    except Exception as e:
        return json.dumps({
            "error": "Search failed",
            "message": str(e)
        })


def main():
    """Run the MCP server"""
    print("Starting MCP SKB Search Server on port 8005...")
    mcp.run(transport="http", port=8005, host="0.0.0.0")


if __name__ == "__main__":
    main()