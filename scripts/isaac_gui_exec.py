"""[ENGINEERING] 使用本机已启用的Kit VS Code执行器；不创建仿真进程。"""
import argparse
import json
import socket
import sys


def execute(source, timeout=45.0):
    # 仅回环地址；无远端主机参数，不能误向其它机器发场景/运动命令。
    with socket.create_connection(('127.0.0.1', 8226), timeout=timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(source.encode('utf-8'))
        chunks = []
        while True:
            block = connection.recv(65536)
            if not block:
                break
            chunks.append(block)
            if sum(map(len, chunks)) > 8_000_000:
                raise ValueError('Unexpectedly large executor response')
    return json.loads(b''.join(chunks).decode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', required=True)
    parser.add_argument('--timeout', type=float, default=45.0)
    args = parser.parse_args()
    reply = execute(args.code, args.timeout)
    print(json.dumps(reply, ensure_ascii=False, indent=2))
    sys.exit(0 if reply.get('status') == 'ok' else 1)
