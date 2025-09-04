import asyncio
from fastmcp import Client

async def main():
    """MCP 클라이언트를 사용하여 서버와 통신합니다."""

    client = Client("http://localhost:8000/mcp")
    print("MCP 클라이언트를 생성하고 서버에 연결합니다.\n")

    try:
        # ① async with 블록을 사용하여 클라이언트 세션을 관리합니다.
        async with client:
            print("--- 사용 가능한 도구 목록 ---")
            tools = await client.list_tools()
            print([tool.name for tool in tools])
            print("")

            # ② 'hello' 도구 테스트
            print("--- 'hello' 도구 테스트 ---")
            response_default = await client.call_tool("hello")
            # call_tool 결과 처리
            if hasattr(response_default, 'content') and response_default.content:
                print(f"기본 호출: {response_default.content[0].text}")
            else:
                print(f"기본 호출: {response_default}")

            response_custom = await client.call_tool("hello", {"name": "헬로월드"})
            if hasattr(response_custom, 'content') and response_custom.content:
                print(f"이름 지정 호출: {response_custom.content[0].text}")
            else:
                print(f"이름 지정 호출: {response_custom}")
            print()

            # ③ 'get_prompt' 도구 테스트
            print("--- 'get_prompt' 도구 테스트 ---")
            prompt_code = await client.call_tool(
                "get_prompt", {"prompt_type": "code_review"}
            )
            if hasattr(prompt_code, 'content') and prompt_code.content:
                print(f"'code_review' 프롬프트:\n{prompt_code.content[0].text}")
            else:
                print(f"'code_review' 프롬프트:\n{prompt_code}")
            print()

            # ④ 'simple://info' 리소스 테스트
            print("--- 'simple://info' 리소스 테스트 ---")
            resource_content = await client.read_resource("simple://info")
            # read_resource 결과 처리
            if hasattr(resource_content, 'content') and resource_content.content:
                print(f"리소스 내용:\n{resource_content.content[0].text}")
            else:
                print(f"리소스 내용:\n{resource_content}")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")


if __name__ == "__main__":
    asyncio.run(main())
