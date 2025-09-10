from mcp.server.fastmcp import FastMCP
import requests
import os
from typing import Dict, List, Any

# ① FastMCP 인스턴스를 생성
mcp = FastMCP("Brave Search MCP Server", host="0.0.0.0", port=11001)

# Brave Search API 설정
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


@mcp.tool()  # ② 도구를 정의합니다.
def hello(name: str = "World") -> str:
    """간단한 인사말을 반환하는 도구"""
    return f"안녕하세요, {name}님!"


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """서버 상태를 확인하는 도구"""
    return {
        "status": "healthy",
        "service": "Brave Search MCP Server",
        "version": "1.0.0",
        "brave_api_configured": bool(BRAVE_API_KEY),
        "available_tools": ["hello", "get_prompt", "brave_search", "health_check"],
        "available_resources": ["simple://info"]
    }


@mcp.tool()
def get_prompt(prompt_type: str = "general") -> str:
    """사전 정의된 프롬프트를 반환하는 도구"""
    prompts = {
        "general": "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 친절하게 답변해주세요.",
        "code_review": "다음 코드를 검토하고 개선점을 제안해주세요. 코드의 가독성, 성능, 보안 측면을 고려해주세요.",
        "translate": "다음 텍스트를 자연스러운 한국어로 번역해주세요.",
        "summarize": "다음 내용을 핵심 포인트 중심으로 간결하게 요약해주세요.",
    }
    return prompts.get(prompt_type, prompts["general"])


@mcp.tool()
def brave_search(query: str, count: int = 10, offset: int = 0, country: str = "KR", language: str = "ko") -> Dict[str, Any]:
    """Brave Search API를 사용하여 웹 검색을 수행하는 도구
    
    Args:
        query: 검색할 키워드 또는 질문
        count: 반환할 결과 수 (기본값: 10, 최대: 20)
        offset: 결과 오프셋 (기본값: 0)
        country: 검색 국가 코드 (기본값: KR)
        language: 검색 언어 코드 (기본값: ko)
    
    Returns:
        검색 결과 딕셔너리 (결과, 메타데이터 포함)
    """
    if not BRAVE_API_KEY:
        return {
            "error": "BRAVE_API_KEY 환경변수가 설정되지 않았습니다.",
            "results": [],
            "total_results": 0
        }
    
    try:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        params = {
            "q": query,
            "count": min(count, 20),  # 최대 20개로 제한
            "offset": offset,
            "country": country,
            "language": language,
            "safesearch": "moderate"
        }
        
        response = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 결과 정리
        results = []
        if "web" in data and "results" in data["web"]:
            for item in data["web"]["results"]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "age": item.get("age", ""),
                    "language": item.get("language", ""),
                    "location": item.get("location", "")
                })
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_metadata": {
                "country": country,
                "language": language,
                "count": len(results),
                "offset": offset
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"검색 요청 중 오류가 발생했습니다: {str(e)}",
            "results": [],
            "total_results": 0
        }
    except Exception as e:
        return {
            "error": f"예상치 못한 오류가 발생했습니다: {str(e)}",
            "results": [],
            "total_results": 0
        }


@mcp.resource("simple://info")  # ③ 리소스를 정의합니다.
def get_server_info() -> str:
    """서버 정보를 제공하는 리소스"""
    return """
    Brave Search MCP Server 정보
    ============================
    
    이 서버는 MCP(Model Context Protocol)를 통해 Brave Search API를 제공하는 서버입니다.
    
    제공하는 도구:
    - hello: 인사말 생성
    - get_prompt: 프롬프트 템플릿 제공
    - brave_search: Brave Search API를 통한 웹 검색
    
    제공하는 리소스:
    - simple://info: 서버 정보
    
    환경 설정:
    - BRAVE_API_KEY: Brave Search API 키 (필수)
    """


if __name__ == "__main__":
    """서버를 실행합니다."""
    # ④ 서버를 실행합니다.
    mcp.run(transport="streamable-http")
