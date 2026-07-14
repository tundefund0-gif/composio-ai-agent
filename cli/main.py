"""Zen Agent CLI — interactive, oneshot, tools search, token stats."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich import box

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import config as zen_config
from core.agent import ZenAgent
from core.llm_client import LLMResponse

app = typer.Typer(help="Zen Agent — AI assistant with 23,790+ Composio tools")
console = Console()


def _get_agent(user_id: str, session_id: Optional[str] = None) -> ZenAgent:
    try:
        return ZenAgent(user_id=user_id, session_id=session_id)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def interactive(
    user: str = typer.Option("cli-user", "--user", "-u", help="User ID"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Existing session ID"),
    no_sandbox: bool = typer.Option(False, "--no-sandbox", help="Disable sandbox"),
):
    """Interactive chat mode with streaming, colored output & token stats."""
    agent = _get_agent(user, session)
    console.print(Panel.fit(
        f"[bold cyan]🧠 Zen Agent[/bold cyan]\n"
        f"Model: {agent._llm.model} | Session: {agent.session_id[:20]}... | "
        f"Max tokens: {agent._llm.max_tokens:,}",
        border_style="cyan",
    ))
    console.print("[dim]Type /clear to reset, /info for stats, /save to save, /load to restore,\n  /export for markdown, /tokens for usage, /quit to exit[/dim]\n")

    while True:
        try:
            prompt = console.input("[bold green]You:[/bold green] ")
        except (EOFError, KeyboardInterrupt):
            break
        if not prompt.strip():
            continue
        if prompt.strip().lower() in ("/quit", "/exit", "/q"):
            break
        if prompt.strip().lower() == "/clear":
            agent.clear_history()
            console.print("[yellow]Conversation cleared.[/yellow]")
            continue
        if prompt.strip().lower() == "/info":
            info = agent.get_info()
            t = Table(box=box.SIMPLE)
            t.add_column("Key", style="cyan")
            t.add_column("Value")
            for k, v in info.items():
                t.add_row(k, str(v))
            console.print(t)
            continue

        if prompt.strip().lower() == "/save":
            path = agent.save_session()
            console.print(f"[green]Session saved to {path}[/green]")
            continue

        if prompt.strip().lower() == "/load":
            # Load most recent session file for this user
            history_dir = Path(config.data_dir) / "conversations"
            if history_dir.exists():
                files = sorted(history_dir.glob(f"{agent.user_id}_*.json"), reverse=True)
                if files:
                    agent.load_session(str(files[0]))
                    console.print(f"[green]Session loaded from {files[0]} ({len(agent.get_history())} messages)[/green]")
                else:
                    console.print("[yellow]No saved sessions found[/yellow]")
            else:
                console.print("[yellow]No saved sessions found[/yellow]")
            continue

        if prompt.strip().lower() == "/export":
            path = agent.export_markdown()
            console.print(f"[green]Conversation exported to {path}[/green]")
            continue

        if prompt.strip().lower() == "/tokens":
            usage = agent.total_token_usage()
            t = Table(box=box.SIMPLE)
            t.add_column("Metric", style="cyan")
            t.add_column("Value")
            t.add_row("Input chars", f"{usage['input_chars']:,}")
            t.add_row("Output chars", f"{usage['output_chars']:,}")
            t.add_row("Tool calls", str(usage['tool_calls']))
            t.add_row("Messages", str(usage['message_count']))
            console.print(t)
            continue

        # Stream response with spinner
        spinner = Spinner("dots", text="[yellow]Thinking...[/yellow]")
        with Live(spinner, refresh_per_second=10, console=console):
            full = ""
            reasoning = ""
            start = time.time()
            for token in agent.chat(prompt, stream=True):
                if token.startswith("__reasoning__"):
                    reasoning += token[13:]
                else:
                    full += token
            elapsed = time.time() - start

        if reasoning:
            with console.status("[dim]Reasoning complete[/dim]"):
                pass

        # Print response as markdown
        console.print()
        md = Markdown(full.strip())
        console.print(Panel(md, border_style="blue", title="[bold]AI[/bold]", title_align="left"))
        console.print(f"[dim]Response time: {elapsed:.1f}s | "
                      f"Length: {len(full):,} chars | "
                      f"History: {len(agent._messages) // 2} turns[/dim]")
        console.print()


@app.command()
def export(
    user: str = typer.Option("cli-user", "--user", "-u"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    fmt: str = typer.Option("markdown", "--format", "-f", help="Export format (markdown)"),
):
    """Export conversation as Markdown."""
    agent = _get_agent(user)
    with console.status("[yellow]Exporting...[/yellow]"):
        path = agent.export_markdown(output)
    console.print(f"[green]Exported to {path}[/green]")

@app.command()
def tokens(
    user: str = typer.Option("cli-user", "--user", "-u"),
):
    """Show token usage statistics."""
    agent = _get_agent(user)
    usage = agent.total_token_usage()
    t = Table(box=box.SIMPLE)
    t.add_column("Metric", style="cyan")
    t.add_column("Value")
    t.add_row("Input chars", f"{usage['input_chars']:,}")
    t.add_row("Output chars", f"{usage['output_chars']:,}")
    t.add_row("Tool calls", str(usage['tool_calls']))
    t.add_row("Messages", str(usage['message_count']))
    console.print(t)

@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="Config key to view"),
):
    """View current configuration."""
    if key:
        val = getattr(zen_config, key, None)
        if val is not None:
            console.print(f"[cyan]{key}:[/cyan] {val}")
        else:
            console.print(f"[red]Unknown config key: {key}[/red]")
    else:
        t = Table(box=box.SIMPLE)
        t.add_column("Key", style="cyan")
        t.add_column("Value")
        for k in dir(zen_config):
            if k.startswith("_"):
                continue
            v = getattr(zen_config, k)
            # Mask keys
            if "key" in k.lower() and v:
                v = v[:12] + "..." if len(v) > 12 else "***"
            t.add_row(k, str(v))
        console.print(t)

@app.command()
def history(
    user: str = typer.Option("cli-user", "--user", "-u"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of messages to show"),
):
    """Show recent conversation history."""
    agent = _get_agent(user)
    msgs = agent.get_history()
    if not msgs:
        console.print("[yellow]No conversation history[/yellow]")
        return
    for msg in msgs[-limit:]:
        role = msg.get("role", "?")
        text = (msg.get("content", "") or "")[:200]
        if role == "user":
            console.print(f"[bold green]You:[/bold green] {text}")
        elif role == "assistant":
            tc = msg.get("tool_calls")
            if tc:
                tools = ", ".join(t.get("function", {}).get("name", "?") for t in tc)
                console.print(f"[bold blue]AI (tools: {tools}):[/bold blue] {text[:100]}")
            else:
                console.print(f"[bold blue]AI:[/bold blue] {text}")
        elif role == "tool":
            console.print(f"[dim]Tool result: {text[:80]}...[/dim]")


@app.command()
def oneshot(
    question: str = typer.Argument(..., help="Single question"),
    user: str = typer.Option("cli-user", "--user", "-u"),
    session: Optional[str] = typer.Option(None, "--session", "-s"),
):
    """Ask a single question (non-streaming)."""
    agent = _get_agent(user, session)
    start = time.time()
    with console.status("[yellow]Processing...[/yellow]"):
        resp = agent.chat(question)
    elapsed = time.time() - start

    if isinstance(resp, LLMResponse):
        md = Markdown(resp.content.strip())
        console.print(Panel(md, border_style="blue", title="[bold]Response[/bold]", title_align="left"))
        if resp.input_tokens or resp.output_tokens:
            console.print(f"[dim]Time: {elapsed:.1f}s | "
                          f"Input: {resp.input_tokens:,} | "
                          f"Output: {resp.output_tokens:,} | "
                          f"Model: {resp.model}[/dim]")
    else:
        console.print(str(resp)[:2000])


@app.command()
def tools(
    query: str = typer.Argument("", help="Search query"),
    user: str = typer.Option("cli-user", "--user", "-u"),
):
    """Search Composio tools."""
    agent = _get_agent(user)
    if query:
        with console.status(f"[yellow]Searching for '{query}'...[/yellow]"):
            result = agent._composio.search_tools(agent.session_id, query)
        data = result.get("data", {})
        results = data.get("results", data.get("tools", []))
        if isinstance(results, list) and results:
            t = Table(box=box.SIMPLE)
            t.add_column("#", style="dim")
            t.add_column("Tool", style="cyan")
            t.add_column("Description")
            for i, r in enumerate(results[:30], 1):
                name = r.get("slug", r.get("name", "?"))
                desc = r.get("description", "")[:100]
                t.add_row(str(i), name, desc)
            console.print(t)
        else:
            console.print("[yellow]No tools found.[/yellow]")
    else:
        with console.status("[yellow]Loading tools...[/yellow]"):
            result = agent._composio.list_all_tools(page=1, page_size=50)
        items = result.get("items", [])
        if items:
            t = Table(box=box.SIMPLE)
            t.add_column("Slug", style="cyan")
            t.add_column("App")
            t.add_column("Description")
            for i in items[:30]:
                slug = i.get("slug", "?")
                app = (i.get("toolkit", {}) or {}).get("name", i.get("app", ""))
                desc = (i.get("description", "") or "")[:80]
                t.add_row(slug, app, desc)
            console.print(t)
            console.print(f"[dim]Showing 30 of {len(items)} tools[/dim]")
        else:
            console.print("[yellow]No tools loaded.[/yellow]")


@app.command()
def session(
    action: str = typer.Argument("info", help="Action: info, reset"),
    user: str = typer.Option("cli-user", "--user", "-u"),
):
    """Manage sessions."""
    agent = _get_agent(user)
    if action == "reset":
        agent.clear_history()
        console.print("[green]Session history cleared.[/green]")
    else:
        info = agent.get_info()
        t = Table(box=box.SIMPLE)
        t.add_column("Key", style="cyan")
        t.add_column("Value")
        for k, v in info.items():
            t.add_row(k, str(v))
        console.print(t)


if __name__ == "__main__":
    app()
