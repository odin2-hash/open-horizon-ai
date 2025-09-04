"""Command line interface for Open Horizon AI system."""

import asyncio
import argparse
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

from .agent import run_open_horizon_agent
from .models import BrainstormRequest, PartnerSearchRequest, ApplicationContentRequest, ErasmusFocusArea
from .agent import run_brainstorming_session, run_partner_search, run_application_writing

console = Console()


def print_header():
    """Print application header."""
    header = """
    # Open Horizon AI
    ## Erasmus+ Project Management System
    
    Transform your project ideas into submission-ready Erasmus+ applications
    through intelligent AI assistance.
    """
    console.print(Panel(Markdown(header), style="blue"))


def print_menu():
    """Print main menu options."""
    table = Table(show_header=False, padding=(0, 2))
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="white")
    
    table.add_row("1", "💡 Brainstorm project ideas")
    table.add_row("2", "🤝 Discover project partners")
    table.add_row("3", "✍️  Generate application content")
    table.add_row("4", "💬 Chat with AI assistant")
    table.add_row("5", "ℹ️  Help and information")
    table.add_row("6", "🚪 Exit")
    
    console.print("\n")
    console.print(Panel(table, title="Main Menu", style="green"))


async def brainstorm_workflow():
    """Interactive brainstorming workflow."""
    console.print("\n[bold blue]🧠 Project Brainstorming Assistant[/bold blue]")
    console.print("Let's develop your Erasmus+ project ideas!\n")
    
    # Get initial concept
    initial_concept = Prompt.ask("What's your initial project idea or concept?", default="")
    if not initial_concept.strip():
        console.print("[red]Please provide an initial concept to get started.[/red]")
        return
    
    # Get focus preference
    console.print("\nErasmus+ Focus Areas:")
    focus_options = [area.value for area in ErasmusFocusArea]
    for i, area in enumerate(focus_options, 1):
        console.print(f"  {i}. {area}")
    
    focus_choice = Prompt.ask(
        "Choose a focus area (1-6) or press Enter to skip", 
        choices=[str(i) for i in range(1, len(focus_options) + 1)] + [""],
        default=""
    )
    
    focus_preference = None
    if focus_choice:
        focus_preference = ErasmusFocusArea(focus_options[int(focus_choice) - 1])
    
    # Create request
    request = BrainstormRequest(
        initial_concept=initial_concept,
        focus_preference=focus_preference,
        organization_context="Swedish NGO Open Horizon"
    )
    
    console.print("\n[yellow]🤔 Analyzing your concept and generating ideas...[/yellow]")
    
    try:
        response = await run_brainstorming_session(request)
        
        if response.success:
            console.print("\n[green]✅ Generated project concepts:[/green]")
            
            for i, concept in enumerate(response.project_concepts, 1):
                panel_content = f"""
**Focus Area:** {concept.focus_area}
**Target Audience:** {concept.target_audience}
**Innovation Angle:** {concept.innovation_angle}
**Feasibility Score:** {concept.feasibility_score}/10
**Rationale:** {concept.rationale}
                """.strip()
                
                console.print(Panel(
                    Markdown(panel_content),
                    title=f"Concept {i}: {concept.title}",
                    style="cyan"
                ))
            
            if response.next_steps:
                console.print("\n[bold]📋 Recommended next steps:[/bold]")
                for step in response.next_steps:
                    console.print(f"  • {step}")
        else:
            console.print(f"[red]❌ Brainstorming failed: {response.error}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error during brainstorming: {str(e)}[/red]")


async def partner_search_workflow():
    """Interactive partner search workflow."""
    console.print("\n[bold blue]🤝 Partner Discovery Assistant[/bold blue]")
    console.print("Let's find the perfect partners for your Erasmus+ project!\n")
    
    project_focus = Prompt.ask("What's the main focus of your project?")
    if not project_focus.strip():
        console.print("[red]Please provide a project focus.[/red]")
        return
    
    # Optional country requirements
    countries_input = Prompt.ask("Required countries (comma-separated, or press Enter to skip)", default="")
    required_countries = [c.strip() for c in countries_input.split(",") if c.strip()] if countries_input else None
    
    # Optional expertise requirements
    expertise_input = Prompt.ask("Required expertise areas (comma-separated, or press Enter to skip)", default="")
    expertise_areas = [e.strip() for e in expertise_input.split(",") if e.strip()] if expertise_input else []
    
    request = PartnerSearchRequest(
        project_focus=project_focus,
        required_countries=required_countries,
        expertise_areas=expertise_areas
    )
    
    console.print("\n[yellow]🔍 Searching for potential partners...[/yellow]")
    
    try:
        response = await run_partner_search(request)
        
        if response.success:
            console.print(f"\n[green]✅ Found {len(response.potential_partners)} potential partners:[/green]")
            
            for partner in response.potential_partners:
                panel_content = f"""
**Country:** {partner.country}
**Type:** {partner.organization_type}
**Expertise:** {', '.join(partner.expertise_areas)}
**Compatibility Score:** {partner.compatibility_score}/10
**Why this partner:** {partner.partnership_rationale}
**Contact:** {partner.contact_info.get('email', 'N/A')}
                """.strip()
                
                console.print(Panel(
                    Markdown(panel_content),
                    title=f"🏢 {partner.name}",
                    style="green"
                ))
            
            metadata = response.search_metadata
            console.print(f"\n[dim]Search covered {len(metadata.get('countries_covered', []))} countries[/dim]")
        else:
            console.print(f"[red]❌ Partner search failed: {response.error}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error during partner search: {str(e)}[/red]")


async def content_generation_workflow():
    """Interactive content generation workflow."""
    console.print("\n[bold blue]✍️ Application Content Generator[/bold blue]")
    console.print("Let's create compelling application text for your Erasmus+ project!\n")
    
    # Section type
    section_types = [
        "Project Description",
        "Methodology", 
        "Impact",
        "Project Management",
        "Dissemination",
        "Budget Justification"
    ]
    
    console.print("Available sections:")
    for i, section in enumerate(section_types, 1):
        console.print(f"  {i}. {section}")
    
    section_choice = Prompt.ask(
        "Choose a section to generate (1-6)",
        choices=[str(i) for i in range(1, len(section_types) + 1)]
    )
    section_type = section_types[int(section_choice) - 1]
    
    # Project context
    project_title = Prompt.ask("Project title")
    focus_area = Prompt.ask("Focus area", default="Digital Transformation")
    target_audience = Prompt.ask("Target audience", default="Young people 18-30")
    
    # Word limit
    word_limit_input = Prompt.ask("Word limit (or press Enter for no limit)", default="")
    word_limit = int(word_limit_input) if word_limit_input.isdigit() else None
    
    project_context = {
        "title": project_title,
        "focus_area": focus_area,
        "target_audience": target_audience
    }
    
    request = ApplicationContentRequest(
        section_type=section_type,
        project_context=project_context,
        word_limit=word_limit
    )
    
    console.print(f"\n[yellow]✍️ Generating {section_type} content...[/yellow]")
    
    try:
        response = await run_application_writing(request)
        
        if response.success and response.generated_content:
            content = response.generated_content
            
            # Display generated content
            console.print(f"\n[green]✅ Generated {section_type}:[/green]")
            console.print(Panel(content.content, style="cyan"))
            
            # Display compliance info
            console.print(f"\n[bold]📊 Content Analysis:[/bold]")
            console.print(f"Word count: {content.word_count}")
            console.print(f"Compliance status: {'✅ Compliant' if content.compliance_status else '⚠️ Needs improvement'}")
            
            if content.compliance_details.strength_areas:
                console.print("\n[green]💪 Strengths:[/green]")
                for strength in content.compliance_details.strength_areas:
                    console.print(f"  • {strength}")
            
            if content.compliance_details.missing_elements:
                console.print("\n[yellow]⚠️ Areas for improvement:[/yellow]")
                for issue in content.compliance_details.missing_elements:
                    console.print(f"  • {issue}")
            
            if content.compliance_details.improvement_suggestions:
                console.print("\n[blue]💡 Suggestions:[/blue]")
                for suggestion in content.compliance_details.improvement_suggestions:
                    console.print(f"  • {suggestion}")
            
        else:
            console.print(f"[red]❌ Content generation failed: {response.error}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error during content generation: {str(e)}[/red]")


async def chat_workflow():
    """Interactive chat with AI assistant."""
    console.print("\n[bold blue]💬 AI Assistant Chat[/bold blue]")
    console.print("Chat with our AI assistant about your Erasmus+ project. Type 'quit' to return to main menu.\n")
    
    # Choose agent type
    agent_types = ["brainstorming", "planning", "application"]
    console.print("Choose assistant type:")
    for i, agent_type in enumerate(agent_types, 1):
        console.print(f"  {i}. {agent_type.title()} Assistant")
    
    agent_choice = Prompt.ask(
        "Choose assistant (1-3)",
        choices=[str(i) for i in range(1, len(agent_types) + 1)],
        default="1"
    )
    selected_agent = agent_types[int(agent_choice) - 1]
    
    console.print(f"\n[green]Connected to {selected_agent.title()} Assistant[/green]")
    console.print("[dim]Type your questions or 'quit' to exit[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask(f"[bold cyan]You[/bold cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            console.print(f"[yellow]{selected_agent.title()} Assistant is thinking...[/yellow]")
            
            response = await run_open_horizon_agent(
                prompt=user_input,
                agent_type=selected_agent
            )
            
            console.print(f"[bold green]Assistant:[/bold green] {response}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]\n")


def show_help():
    """Show help information."""
    help_text = """
    # Open Horizon AI Help
    
    ## What is Open Horizon AI?
    Open Horizon AI is an intelligent assistant system designed to help Swedish NGO "Open Horizon" 
    and similar organizations create successful Erasmus+ project applications.
    
    ## Features:
    - **Project Brainstorming**: Generate innovative project ideas aligned with Erasmus+ priorities
    - **Partner Discovery**: Find suitable European partners for your projects
    - **Application Writing**: Create compelling, compliant application text
    - **AI Chat**: Get expert guidance throughout the application process
    
    ## Erasmus+ Focus Areas:
    - Digital Transformation
    - Green Transition  
    - Inclusion and Diversity
    - Participation
    - European Values
    - Innovation
    
    ## Getting Started:
    1. Start with brainstorming to develop your project concept
    2. Use partner discovery to find suitable collaborators
    3. Generate application content section by section
    4. Use the chat feature for specific questions and guidance
    
    ## Tips for Success:
    - Be specific about your target audience and intended impact
    - Consider European added value in all project elements
    - Ensure partner complementarity, not just geographic diversity
    - Follow Erasmus+ Programme Guide requirements closely
    """
    
    console.print(Panel(Markdown(help_text), title="Help & Information", style="blue"))


async def main():
    """Main CLI application loop."""
    print_header()
    
    while True:
        try:
            print_menu()
            choice = Prompt.ask(
                "\n[bold]Choose an option[/bold]",
                choices=["1", "2", "3", "4", "5", "6"],
                default="1"
            )
            
            if choice == "1":
                await brainstorm_workflow()
            elif choice == "2":
                await partner_search_workflow()
            elif choice == "3":
                await content_generation_workflow()
            elif choice == "4":
                await chat_workflow()
            elif choice == "5":
                show_help()
            elif choice == "6":
                console.print("\n[green]Thank you for using Open Horizon AI! 👋[/green]")
                break
            
            # Ask if user wants to continue
            if choice != "6":
                continue_choice = Confirm.ask("\nReturn to main menu?", default=True)
                if not continue_choice:
                    break
                    
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]An error occurred: {str(e)}[/red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open Horizon AI - Erasmus+ Project Management System")
    parser.add_argument("--version", action="version", version="Open Horizon AI 1.0.0")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)