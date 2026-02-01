#!/usr/bin/env python3
"""
Academic Research Agent - Core utilities for systematic literature search.

Usage:
    python research_agent.py generate-queries "your topic"
    python research_agent.py classify-url "https://example.com/paper"
    python research_agent.py format-report "topic" sources.json
"""

import json
import re
import sys
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import IntEnum


class SourcePriority(IntEnum):
    """Source hierarchy - lower number = higher priority"""
    PEER_REVIEWED = 1
    JOURNAL_ARTICLE = 2
    THESIS_WORKING_PAPER = 3
    INDEPENDENT_ORG = 4
    COMPANY_INDUSTRY = 5
    OTHER_WEB = 6


# Domain patterns for source classification
SOURCE_PATTERNS = {
    SourcePriority.PEER_REVIEWED: [
        r'doi\.org', r'pubmed\.ncbi\.nlm\.nih\.gov', r'ncbi\.nlm\.nih\.gov/pmc',
        r'nature\.com', r'sciencedirect\.com', r'springer\.com', r'wiley\.com',
        r'tandfonline\.com', r'sagepub\.com', r'jstor\.org', r'cell\.com',
        r'acs\.org', r'ieee\.org', r'acm\.org',
    ],
    SourcePriority.JOURNAL_ARTICLE: [
        r'scholar\.google', r'researchgate\.net', r'academia\.edu',
        r'semanticscholar\.org', r'arxiv\.org', r'ssrn\.com',
        r'biorxiv\.org', r'medrxiv\.org',
    ],
    SourcePriority.THESIS_WORKING_PAPER: [
        r'\.edu/', r'repository\.', r'dspace\.', r'etd\.',
        r'proquest\.com', r'nber\.org',
    ],
    SourcePriority.INDEPENDENT_ORG: [
        r'who\.int', r'un\.org', r'oecd\.org', r'worldbank\.org', r'imf\.org',
        r'europa\.eu', r'\.gov/', r'pewresearch\.org', r'brookings\.edu', r'rand\.org',
    ],
    SourcePriority.COMPANY_INDUSTRY: [
        r'mckinsey\.com', r'deloitte\.com', r'pwc\.com', r'bcg\.com',
        r'gartner\.com', r'forrester\.com', r'statista\.com',
    ],
}

PRIORITY_NAMES = {
    SourcePriority.PEER_REVIEWED: "Peer-reviewed journals",
    SourcePriority.JOURNAL_ARTICLE: "Journal articles/preprints",
    SourcePriority.THESIS_WORKING_PAPER: "Theses/working papers",
    SourcePriority.INDEPENDENT_ORG: "Independent organizations",
    SourcePriority.COMPANY_INDUSTRY: "Company/industry sources",
    SourcePriority.OTHER_WEB: "Other web sources",
}


@dataclass
class Source:
    """Represents a research source with metadata"""
    url: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    publication: Optional[str] = None
    doi: Optional[str] = None
    priority: int = 6
    abstract: Optional[str] = None
    reliability_notes: list[str] = field(default_factory=list)

    def to_apa(self) -> str:
        """Generate APA 7th edition citation"""
        if not self.authors:
            author_str = "Unknown Author"
        elif len(self.authors) == 1:
            author_str = self.authors[0]
        elif len(self.authors) == 2:
            author_str = f"{self.authors[0]} & {self.authors[1]}"
        else:
            author_str = f"{self.authors[0]} et al."

        year_str = f"({self.year})" if self.year else "(n.d.)"

        # For journal articles: article title is plain, journal name is italicized
        # For books/reports: title is italicized
        if self.publication:
            title_str = self.title  # Article title: sentence case, no italics
            pub_str = f"*{self.publication}*"  # Journal name: italicized
        else:
            title_str = f"*{self.title}*"  # Book/report title: italicized
            pub_str = None

        parts = [author_str, year_str, title_str]
        if pub_str:
            parts.append(pub_str)
        if self.doi:
            parts.append(f"https://doi.org/{self.doi}")
        elif self.url:
            parts.append(self.url)

        return ". ".join(parts)

    def inline_citation(self) -> str:
        """Generate inline citation"""
        if not self.authors:
            author = "Unknown"
        elif len(self.authors) >= 3:
            author = self.authors[0].split()[-1] + " et al."
        elif len(self.authors) == 2:
            author = f"{self.authors[0].split()[-1]} & {self.authors[1].split()[-1]}"
        else:
            author = self.authors[0].split()[-1]

        year = self.year if self.year else "n.d."
        return f"({author}, {year})"


def classify_source(url: str) -> int:
    """Determine source priority (1-6) based on URL patterns"""
    url_lower = url.lower()
    for priority, patterns in SOURCE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return int(priority)
    return int(SourcePriority.OTHER_WEB)


def generate_search_queries(topic: str) -> list[dict]:
    """Generate prioritized search queries for a topic"""
    queries = []

    # Academic database searches (highest priority)
    academic_sites = [
        ("scholar.google.com", "Google Scholar"),
        ("pubmed.ncbi.nlm.nih.gov", "PubMed"),
        ("semanticscholar.org", "Semantic Scholar"),
    ]

    for site, name in academic_sites:
        queries.append({
            "query": f"site:{site} {topic}",
            "source": name,
            "priority": 1
        })

    # Preprint servers
    queries.append({
        "query": f"site:arxiv.org OR site:ssrn.com {topic}",
        "source": "Preprint servers",
        "priority": 2
    })

    # Institutional repositories
    queries.append({
        "query": f"site:edu {topic} research paper",
        "source": "University repositories",
        "priority": 3
    })

    # Government and international orgs
    queries.append({
        "query": f"site:gov OR site:un.org OR site:who.int {topic}",
        "source": "Government/Intl orgs",
        "priority": 4
    })

    # General academic search
    queries.append({
        "query": f"{topic} peer-reviewed research study",
        "source": "General academic",
        "priority": 5
    })

    return queries


def format_markdown_report(topic: str, sources: list[dict], findings: dict[str, str],
                           uncertainties: list[str], methodology_notes: list[str]) -> str:
    """Generate a Markdown research report"""
    now = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Research Report: {topic}",
        "",
        f"**Query:** {topic}",
        f"**Date:** {now}",
        f"**Agent Version:** 1.0",
        f"**Sources Found:** {len(sources)}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "[Synthesize key findings here]",
        "",
        "## Methodology",
        "",
        "### Search Strategy",
        ""
    ]

    for note in methodology_notes:
        lines.append(f"- {note}")

    lines.extend([
        "",
        "### Source Distribution",
        "",
        "| Priority Level | Count | Type |",
        "|----------------|-------|------|",
    ])

    # Count sources by priority
    priority_counts = {}
    for source in sources:
        p = source.get('priority', 6)
        priority_counts[p] = priority_counts.get(p, 0) + 1

    for i in range(1, 7):
        count = priority_counts.get(i, 0)
        lines.append(f"| {i} | {count} | {PRIORITY_NAMES.get(SourcePriority(i), 'Unknown')} |")

    lines.extend(["", "## Findings", ""])

    for section_title, content in findings.items():
        lines.extend([f"### {section_title}", "", content, ""])

    lines.extend([
        "## Source Quality Assessment",
        "",
        "| Source | Type | Priority | Reliability Notes |",
        "|--------|------|----------|-------------------|",
    ])

    sorted_sources = sorted(sources, key=lambda s: s.get('priority', 6))
    for source in sorted_sources:
        notes = "; ".join(source.get('reliability_notes', [])) or "—"
        title = source.get('title', 'Untitled')
        short_title = title[:40] + "..." if len(title) > 40 else title
        priority = source.get('priority', 6)
        type_name = PRIORITY_NAMES.get(SourcePriority(priority), 'Other')
        lines.append(f"| {short_title} | {type_name} | {priority} | {notes} |")

    lines.extend(["", "## Uncertainties and Limitations", ""])

    if uncertainties:
        for u in uncertainties:
            lines.append(f"- {u}")
    else:
        lines.append("- No significant uncertainties identified")

    lines.extend(["", "## References", ""])

    # Sort alphabetically by first author
    sorted_refs = sorted(sources, key=lambda s: (s.get('authors') or ['ZZZ'])[0])
    for source in sorted_refs:
        src = Source(**{k: v for k, v in source.items() if k in Source.__dataclass_fields__})
        lines.append(f"- {src.to_apa()}")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python research_agent.py generate-queries 'topic'")
        print("  python research_agent.py classify-url 'url'")
        print("  python research_agent.py format-report 'topic' sources.json")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate-queries":
        if len(sys.argv) < 3:
            print("Error: Topic required")
            sys.exit(1)
        topic = " ".join(sys.argv[2:])
        queries = generate_search_queries(topic)
        print(json.dumps(queries, indent=2))

    elif command == "classify-url":
        if len(sys.argv) < 3:
            print("Error: URL required")
            sys.exit(1)
        url = sys.argv[2]
        priority = classify_source(url)
        print(json.dumps({
            "url": url,
            "priority": priority,
            "type": PRIORITY_NAMES.get(SourcePriority(priority), "Unknown")
        }, indent=2))

    elif command == "format-report":
        if len(sys.argv) < 4:
            print("Error: Topic and sources.json required")
            sys.exit(1)
        topic = sys.argv[2]
        with open(sys.argv[3]) as f:
            data = json.load(f)
        report = format_markdown_report(
            topic,
            data.get('sources', []),
            data.get('findings', {}),
            data.get('uncertainties', []),
            data.get('methodology_notes', [])
        )
        print(report)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
