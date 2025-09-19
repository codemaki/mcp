#!/usr/bin/env python3
"""
SSH MCP Tool 테스트 스크립트
"""
import asyncio
import sys
import os

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from example_server import ssh_execute, get_server_processes, get_server_status

async def test_ssh_tools():
    """SSH 도구들을 테스트합니다."""
    
    print("=== SSH MCP Tool 테스트 ===")
    print()
    
    # 테스트용 PEM 키 데이터 (실제로는 유효한 키가 필요)
    test_pem_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdef...
(이것은 테스트용 더미 키입니다)
-----END RSA PRIVATE KEY-----"""
    
    # 1. SSH 연결 테스트 (실제 서버 없이는 실패할 것임)
    print("1. SSH 연결 테스트")
    result = await ssh_execute(
        hostname="127.0.0.1",  # localhost 테스트
        command="echo 'Hello World'",
        username="testuser",
        pem_key_data=test_pem_key
    )
    print(f"결과: {result}")
    print()
    
    # 2. 프로세스 조회 테스트
    print("2. 프로세스 조회 테스트")
    result = await get_server_processes(
        hostname="127.0.0.1",
        username="testuser", 
        pem_key_data=test_pem_key
    )
    print(f"결과: {result}")
    print()
    
    # 3. 서버 상태 조회 테스트
    print("3. 서버 상태 조회 테스트")
    result = await get_server_status(
        hostname="127.0.0.1",
        username="testuser",
        pem_key_data=test_pem_key
    )
    print(f"결과: {result}")
    print()
    
    print("=== 테스트 완료 ===")
    print("실제 SSH 서버와 유효한 PEM 키가 있다면 정상적으로 동작할 것입니다.")

if __name__ == "__main__":
    asyncio.run(test_ssh_tools())
