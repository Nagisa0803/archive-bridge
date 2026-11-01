"""Native portable entry point. Never accepts credentials as command-line arguments."""

import argparse, json, os, sys, webbrowser
from pathlib import Path
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Archive Bridge: local account exporter for Archive Lens."
    )
    parser.add_argument(
        "--version", action="version", version="Archive Bridge " + __version__
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Folder for local exports (default: ArchiveBridgeData beside the executable).",
    )
    parser.add_argument(
        "--port", type=int, default=0, help="Local port, 0 chooses a free port."
    )
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Offline protocol and ZIP round-trip self-test; no account or network access.",
    )
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    default = (
        Path(sys.executable).resolve().parent
        if getattr(sys, "frozen", False)
        else Path.cwd()
    )
    data = (args.data_dir or default / "ArchiveBridgeData").resolve()
    data.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.self_test:
        from .selftest import run

        print(json.dumps(run(data)))
        return
    from .server import Application, create_server

    app = Application(data)
    try:
        server = create_server(app, args.port)
    except OSError:
        parser.exit(
            2, "Could not open the requested local port. Choose another --port.\n"
        )
    url = f"http://127.0.0.1:{server.server_port}/#" + app.token
    print("Archive Bridge " + __version__ + " | Local only")
    print("Exports: " + str(app.output))
    if args.no_browser:
        print("Private local access URL: do not share this active link.")
        print("Open: " + url, flush=True)
    else:
        print(
            "Opening the local wizard. Its private access link is not printed.",
            flush=True,
        )
        if not webbrowser.open(url):
            print(
                "Browser did not open. Restart with --no-browser for a private manual URL.",
                flush=True,
            )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        app.cancel.set()
        server.server_close()
        app.project = None


if __name__ == "__main__":
    main()
