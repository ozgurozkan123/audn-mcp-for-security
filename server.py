import os
import subprocess
import shlex
from typing import Optional
from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("katana-mcp")


@mcp.tool()
def do_katana(
    target: list[str],
    exclude: Optional[list[str]] = None,
    depth: Optional[int] = None,
    js_crawl: Optional[bool] = None,
    jsluice: Optional[bool] = None,
    headers: Optional[list[str]] = None,
    strategy: Optional[str] = None,
    headless: Optional[bool] = None,
    system_chrome: Optional[bool] = None,
    show_browser: Optional[bool] = None,
) -> str:
    """
    Performs fast and configurable web crawling on the given target URLs,
    identifying endpoints, parameters, and JS-based links using Katana.

    Args:
        target: List of target URLs (e.g., https://example.com) to scan for endpoints and JavaScript-based links.
        exclude: List of URLs or regex patterns to exclude from crawling.
        depth: Maximum crawl depth (e.g., 3 for three levels deep).
        js_crawl: Enable crawling and endpoint extraction from JavaScript files.
        jsluice: Enable JSluice parsing for deeper JavaScript-based link analysis (memory intensive).
        headers: List of custom headers or cookies to include in requests (format: Header:Value).
        strategy: Crawling strategy to use: 'depth-first' or 'breadth-first' (default is depth-first).
        headless: Enable headless browser-based hybrid crawling (experimental).
        system_chrome: Use the locally installed Chrome browser instead of the built-in one.
        show_browser: Show the browser window even in headless mode (for debugging/visual inspection).
    """
    # Build the katana command
    katana_args = ["katana", "-u", ",".join(target), "-silent"]

    if exclude and len(exclude) > 0:
        katana_args.extend(["-exclude", ",".join(exclude)])

    if depth is not None:
        katana_args.extend(["-d", str(depth)])

    if js_crawl:
        katana_args.append("-jc")

    if jsluice:
        katana_args.append("-jsl")

    if headers and len(headers) > 0:
        for header in headers:
            katana_args.extend(["-H", header])

    if strategy:
        katana_args.extend(["-strategy", strategy])

    if headless:
        katana_args.append("-headless")

    if system_chrome:
        katana_args.append("-system-chrome")

    if show_browser:
        katana_args.append("-show-browser")

    try:
        # Execute katana command
        result = subprocess.run(
            katana_args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr

        if not output.strip():
            return "Katana completed but returned no output. The target may not have any crawlable endpoints."

        return output

    except subprocess.TimeoutExpired:
        return "Error: Katana execution timed out after 5 minutes."
    except FileNotFoundError:
        return "Error: Katana binary not found. Please ensure katana is installed."
    except Exception as e:
        return f"Error executing katana: {str(e)}"


# Run the server
if __name__ == "__main__":
    # Get port from environment (Render sets this automatically)
    port = int(os.getenv("PORT", 8000))

    mcp.run(
        transport="sse",  # SSE transport for remote connections
        host="0.0.0.0",  # MUST bind to 0.0.0.0 for containers
        port=port,  # Use PORT from environment
        path="/mcp",  # MCP endpoint path (SSE at /mcp/sse, HTTP at /mcp)
    )
