import os
import time
import aiohttp
import asyncio
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from dotenv import load_dotenv

load_dotenv()
smsAPIroute = os.getenv("smsAPIroute")

console = Console()

async def send_sms_async(session, account, password, number, content, smstype=0, mmstitle=""):
    url = smsAPIroute
    payload = {
        "account": account,
        "password": password,
        "numbers": number,
        "content": content,
        "smstype": smstype,
        "mmstitle": mmstitle
    }
    headers = {
        "Content-Type": "application/json;charset=utf-8"
    }

    try:
        async with session.post(url, json=payload, headers=headers, timeout=10) as response:
            response.raise_for_status()
            return True
    except aiohttp.ClientError as http_err:
        console.print(f"[bold red]HTTP error occurred while sending to {number}:[/bold red] {http_err}")
    except asyncio.TimeoutError:
        console.print(f"[bold red]Timeout error occurred while sending SMS to {number}[/bold red]")
    except Exception as err:
        console.print(f"[bold red]An unexpected error occurred while sending to {number}:[/bold red] {err}")
    return False

async def send_all(account, password, numbers, content):
    success_count = 0
    fail_count = 0

    async with aiohttp.ClientSession() as session:
        with Progress(
            SpinnerColumn(spinner_name="hearts"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[blue]{task.completed}/[green]{task.total} [green]Sent"),
            console=console
        ) as progress:
            task_id = progress.add_task("[cyan]Sending messages...", total=len(numbers))

            for number in numbers:
                success = await send_sms_async(session, account, password, number, content)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                progress.advance(task_id)

                await asyncio.sleep(2)

    return success_count, fail_count

def load_numbers_from_file(filename):
    while True:
        try:
            with open(filename, 'r') as file:
                numbers = [line.strip() for line in file if line.strip()]
            if not numbers:
                console.print(f"[bold yellow]Warning: No phone numbers found in {filename}[/bold yellow]")
            return numbers
        except FileNotFoundError:
            console.print(f"[bold red]Error: The file '{filename}' was not found.[/bold red]")
            filename = Prompt.ask("[bold green]Please re-enter the correct phone numbers file path[/bold green]")
        except Exception as err:
            console.print(f"[bold red]Error reading file '{filename}':[/bold red] {err}")
            filename = Prompt.ask("[bold green]Please re-enter the correct phone numbers file path[/bold green]")

def load_message_from_file(filename):
    while True:
        try:
            with open(filename, 'r') as file:
                message = file.read().strip()
            if not message:
                console.print(f"[bold yellow]Warning: No messages found in {filename}[/bold yellow]")
            return message
        except FileNotFoundError:
            console.print(f"[bold red]Error: The file '{filename}' was not found.[/bold red]")
            filename = Prompt.ask("[bold green]Please re-enter the correct messages file path[/bold green]")
        except Exception as err:
            console.print(f"[bold red]Error reading file '{filename}':[/bold red] {err}")
            filename = Prompt.ask("[bold green]Please re-enter the correct messages file path[/bold green]")

async def display_settings(account, password):
    settings_panel = Panel(
        f"[bold blue]Account:[/bold blue] {account}\n[bold blue]Password:[/bold blue] {'*' * len(password)}",
        title="Settings",
        title_align="left",
        border_style="blue",
        expand=False
    )
    console.print(settings_panel)

async def main():
    console.print(Panel("Welcome to Rocket SMS Sender 🚀", title="Rocket SMS Sender 🚀", title_align="center", border_style="green"))

    account = Prompt.ask("[bold green]Enter your SMS account[/bold green]")
    password = Prompt.ask("[bold green]Enter your SMS password[/bold green]")

    await display_settings(account, password)

    numbers_file = Prompt.ask("[bold green]Enter the phone numbers file path[/bold green]", default="numbers.txt")
    numbers = load_numbers_from_file(numbers_file)
    if not numbers:
        console.print("[bold red]No phone numbers to send messages to. Exiting...[/bold red]")
        return

    messages_file = Prompt.ask("[bold green]Enter the messages file path[/bold green]", default="message.txt")
    message = load_message_from_file(messages_file)
    if not message:
        console.print("[bold red]No messages to send. Exiting...[/bold red]")
        return

    console.print(f"[bold green]Loaded {len(numbers)} phone numbers and the message to be sent.[/bold green]")

    # Confirm before sending
    confirm_send = Confirm.ask("[bold yellow]Do you want to proceed with sending the SMS messages?[/bold yellow]")
    if not confirm_send:
        console.print("[bold red]Operation canceled. Exiting...[/bold red]")
        time.sleep(2)
        console.print("[bold red]Exited[/bold red]")
        return

    console.print(f"[bold green]Sending messages to {len(numbers)} phone numbers...[/bold green]")

    success_count, fail_count = await send_all(account, password, numbers, message)

    if success_count > 0:
        success_panel = Panel(
            f"Messages successfully sent to {success_count} numbers.✅",
            title="Success",
            border_style="yellow",
            expand=False
        )
        console.print(success_panel)

    if fail_count > 0:
        failure_panel = Panel(
            f"Failed to send to {fail_count} numbers.❌",
            title="Failure",
            border_style="red",
            expand=False
        )
        console.print(failure_panel)

if __name__ == "__main__":
    asyncio.run(main())