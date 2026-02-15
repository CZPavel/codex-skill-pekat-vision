"""Demo client for Projects Manager Simple TCP server.

Common command patterns:
- start:<project_path>  -> done | error:port | not-found
- stop:<project_path>   -> done
- status:<project_path> -> stopped|stopping|starting|running
- switch:<project_path> -> success
"""

import socket


def send_cmd(host: str, port: int, cmd: str, recv_bytes: int = 64, timeout_s: float = 3.0) -> str:
    with socket.create_connection((host, port), timeout=timeout_s) as sock:
        sock.settimeout(timeout_s)
        sock.sendall(cmd.encode("utf-8"))
        response = sock.recv(recv_bytes)
        return response.decode("utf-8", errors="replace").strip()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 7002  # nastav podle Projects Manager settings
    PROJECT_PATH = r"C:\Users\pekat\PekatVisionProjects\Test Project 1"

    print("Status:", send_cmd(HOST, PORT, f"status:{PROJECT_PATH}"))
    # print("Start :", send_cmd(HOST, PORT, f"start:{PROJECT_PATH}"))
    # print("Stop  :", send_cmd(HOST, PORT, f"stop:{PROJECT_PATH}"))
