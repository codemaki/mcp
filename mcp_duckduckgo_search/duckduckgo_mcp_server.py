import asyncio
import json
import random
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup

# FastMCP 인스턴스를 생성 (포트 11005 사용)
mcp = FastMCP("DuckDuckGo Search MCP Server", host="0.0.0.0", port=11005)


class DuckDuckGoSearcher:
    """DuckDuckGo 검색을 위한 클래스"""
    
    def __init__(self):
        self.base_url = "https://duckduckgo.com"
        self.lite_url = "https://lite.duckduckgo.com/lite"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
    
    def _get_headers(self) -> Dict[str, str]:
        """랜덤한 User-Agent를 포함한 헤더를 반환합니다."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'identity',  # 압축 비활성화
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def search_web_lite(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """DuckDuckGo Lite를 사용한 웹 검색 (더 안정적)"""
        try:
            # 짧은 지연 추가 (봇 탐지 방지)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(15.0),
                follow_redirects=True
            ) as client:
                # POST 방식으로 검색 (더 안정적)
                data = {
                    'q': query,
                    'kl': 'kr-kr'
                }
                
                response = await client.post(
                    self.lite_url,
                    data=data,
                    headers=self._get_headers(),
                )
                
                if response.status_code != 200:
                    print(f"HTTP 오류: {response.status_code}")
                    return await self._fallback_search(query, max_results)
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # DuckDuckGo Lite의 검색 결과 구조 파싱
                result_elements = soup.find_all('tr')
                
                for i, element in enumerate(result_elements):
                    try:
                        # 링크 찾기
                        link_elem = element.find('a', href=True)
                        if not link_elem:
                            continue
                            
                        url = link_elem.get('href', '')
                        if not url or url.startswith('/'):
                            continue
                            
                        title = link_elem.get_text(strip=True)
                        if not title:
                            continue
                        
                        # 설명 찾기 (같은 행의 다른 td 또는 다음 행에서)
                        description = ""
                        
                        # 먼저 같은 행에서 설명 찾기
                        td_elements = element.find_all('td')
                        if len(td_elements) > 1:
                            for td in td_elements[1:]:  # 첫 번째 td는 보통 링크
                                desc_text = td.get_text(strip=True)
                                if desc_text and desc_text != title:
                                    description = desc_text
                                    break
                        
                        # 다음 행에서도 설명 찾기
                        if not description:
                            next_row = element.find_next_sibling('tr')
                            if next_row:
                                desc_elem = next_row.find('td')
                                if desc_elem:
                                    desc_text = desc_elem.get_text(strip=True)
                                    # 링크가 아닌 텍스트만 설명으로 사용
                                    if desc_text and not next_row.find('a', href=True):
                                        description = desc_text
                        
                        if title and url:
                            results.append({
                                'title': title,
                                'url': url,
                                'description': description or "설명 없음"
                            })
                            
                            if len(results) >= max_results:
                                break
                                
                    except Exception as e:
                        print(f"결과 파싱 중 오류: {e}")
                        continue
                
                return results
                
        except Exception as e:
            print(f"Lite 검색 중 오류: {e}")
            return await self._fallback_search(query, max_results)
    
    async def _fallback_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """대안 검색 방법"""
        try:
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(20.0),
                follow_redirects=True
            ) as client:
                # 간단한 GET 방식으로 시도
                params = {
                    'q': query,
                    'ia': 'web'
                }
                
                response = await client.get(
                    f"{self.base_url}/",
                    params=params,
                    headers=self._get_headers(),
                )
                
                if response.status_code != 200:
                    return []
                
                # 기본적인 HTML 파싱 시도
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # 다양한 셀렉터로 검색 결과 찾기
                selectors = [
                    'article[data-testid="result"]',
                    'div[data-testid="result"]',
                    '.result',
                    '.web-result',
                    'div.result__body',
                    'li[data-layout="organic"]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        for element in elements[:max_results]:
                            try:
                                # 제목과 링크 찾기
                                title_elem = element.select_one('h3 a, h2 a, .result__title a, a[data-testid="result-title-a"]')
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                url = title_elem.get('href', '')
                                
                                # 설명 찾기
                                desc_elem = element.select_one('.result__snippet, [data-testid="result-snippet"], .snippet')
                                description = desc_elem.get_text(strip=True) if desc_elem else "설명 없음"
                                
                                if title and url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'description': description
                                    })
                                    
                            except Exception as e:
                                print(f"대안 파싱 중 오류: {e}")
                                continue
                        
                        if results:
                            break
                
                return results
                
        except Exception as e:
            print(f"대안 검색 중 오류: {e}")
            return []
    
    async def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """웹 검색을 수행합니다."""
        # 먼저 Lite 버전 시도
        results = await self.search_web_lite(query, max_results)
        
        # 결과가 없으면 대안 방법 시도
        if not results:
            results = await self._fallback_search(query, max_results)
        
        # 검색 결과가 없는 경우
        if not results:
            return []
        
        return results
    
    async def search_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """즉석 답변을 검색합니다."""
        try:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                params = {
                    'q': query,
                    'format': 'json',
                    'no_redirect': '1',
                    'no_html': '1',
                    'skip_disambig': '1'
                }
                
                response = await client.get(
                    f"{self.base_url}/",
                    params=params,
                    headers=self._get_headers(),
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # 즉석 답변이 있는지 확인
                        if data.get('AbstractText'):
                            return {
                                'answer': data.get('AbstractText'),
                                'source': data.get('AbstractSource', ''),
                                'url': data.get('AbstractURL', ''),
                                'type': 'abstract'
                            }
                        elif data.get('Answer'):
                            return {
                                'answer': data.get('Answer'),
                                'source': data.get('AnswerType', ''),
                                'url': '',
                                'type': 'answer'
                            }
                    except json.JSONDecodeError:
                        print("JSON 파싱 오류")
                
                return None
                
        except Exception as e:
            print(f"즉석 답변 검색 중 오류: {e}")
            return None


# DuckDuckGo 검색기 인스턴스 생성
searcher = DuckDuckGoSearcher()


@mcp.tool()
async def search_web(query: str, max_results: int = 10) -> str:
    """
    DuckDuckGo를 사용하여 웹 검색을 수행합니다.
    
    Args:
        query: 검색할 키워드
        max_results: 반환할 최대 결과 수 (기본값: 10)
    
    Returns:
        검색 결과를 JSON 형태의 문자열로 반환
    """
    try:
        results = await searcher.search_web(query, max_results)
        
        if not results:
            return json.dumps({
                'status': 'success',
                'query': query,
                'results_count': 0,
                'results': [],
                'message': '검색 결과가 없습니다.'
            }, ensure_ascii=False, indent=2)
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'results_count': len(results),
            'results': results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'query': query,
            'error': str(e),
            'message': '검색 중 오류가 발생했습니다.'
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def search_instant_answer(query: str) -> str:
    """
    DuckDuckGo의 즉석 답변 기능을 사용하여 직접적인 답변을 검색합니다.
    
    Args:
        query: 검색할 질문이나 키워드
    
    Returns:
        즉석 답변을 JSON 형태의 문자열로 반환
    """
    try:
        result = await searcher.search_instant_answer(query)
        
        if not result:
            return json.dumps({
                'status': 'success',
                'query': query,
                'has_answer': False,
                'message': '즉석 답변을 찾을 수 없습니다.'
            }, ensure_ascii=False, indent=2)
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'has_answer': True,
            'answer': result
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'query': query,
            'error': str(e),
            'message': '즉석 답변 검색 중 오류가 발생했습니다.'
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def search_combined(query: str, max_results: int = 5) -> str:
    """
    즉석 답변과 웹 검색을 동시에 수행하여 통합된 결과를 제공합니다.
    
    Args:
        query: 검색할 키워드나 질문
        max_results: 웹 검색 결과의 최대 개수 (기본값: 5)
    
    Returns:
        즉석 답변과 웹 검색 결과를 포함한 통합 결과를 JSON 형태로 반환
    """
    try:
        # 동시에 두 검색 수행
        instant_task = searcher.search_instant_answer(query)
        web_task = searcher.search_web(query, max_results)
        
        instant_result, web_results = await asyncio.gather(instant_task, web_task)
        
        return json.dumps({
            'status': 'success',
            'query': query,
            'instant_answer': instant_result,
            'web_results': {
                'count': len(web_results),
                'results': web_results
            }
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'query': query,
            'error': str(e),
            'message': '통합 검색 중 오류가 발생했습니다.'
        }, ensure_ascii=False, indent=2)


@mcp.resource("duckduckgo://info")
def get_server_info() -> str:
    """서버 정보를 제공하는 리소스"""
    return """
    DuckDuckGo Search MCP Server 정보
    =================================
    
    이 서버는 DuckDuckGo 검색 엔진을 활용하여 웹 검색과 즉석 답변 기능을 제공합니다.
    
    제공하는 도구:
    - search_web: 일반 웹 검색 (최대 결과 수 지정 가능)
    - search_instant_answer: 즉석 답변 검색 (계산, 정의, 간단한 질문 등)
    - search_combined: 즉석 답변과 웹 검색을 동시에 수행
    
    제공하는 리소스:
    - duckduckgo://info: 서버 정보
    
    포트: 11005
    프로토콜: MCP (Model Context Protocol)
    """


@mcp.resource("duckduckgo://usage")
def get_usage_examples() -> str:
    """사용 예시를 제공하는 리소스"""
    return """
    DuckDuckGo Search MCP Server 사용 예시
    ====================================
    
    1. 일반 웹 검색:
       search_web("파이썬 튜토리얼", max_results=5)
    
    2. 즉석 답변 검색:
       search_instant_answer("2+2는 무엇인가요?")
       search_instant_answer("서울의 인구는?")
    
    3. 통합 검색:
       search_combined("인공지능이란 무엇인가", max_results=3)
    
    검색 결과는 모두 JSON 형태로 반환되며, 한국어를 지원합니다.
    """


if __name__ == "__main__":
    """서버를 실행합니다."""
    print("DuckDuckGo Search MCP Server 시작 중...")
    print("포트: 11005")
    print("프로토콜: streamable-http")
    
    # 서버를 실행합니다.
    mcp.run(transport="streamable-http")
