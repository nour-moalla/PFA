"""
Resume Parser Module
Extracts and structures resume data from PDF files
"""

import re
from typing import Dict, List, Optional
import pdfplumber
from pathlib import Path


class ResumeParser:
    """Parse and structure resume content from PDF files"""

    def __init__(self):
        # Common section headers (case-insensitive)
        self.section_patterns = {
            'contact': r'(contact|email|phone|address|linkedin|github)',
            'summary': r'(summary|profile|objective|about)',
            'experience': r'(experience|employment|work history|professional experience)',
            'education': r'(education|academic|degree|university|college)',
            'skills': r'(skills|technical skills|competencies|expertise|technologies)',
            'certifications': r'(certifications?|licenses?|credentials)',
            'projects': r'(projects?|portfolio)',
            'achievements': r'(achievements?|awards?|honors?|accomplishments?)'
        }

        # Patterns for extracting specific data
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        self.url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'

        # Common skills to look for
        self.common_tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'spring', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'terraform', 'jenkins', 'git', 'ci/cd', 'sql',
            'mongodb', 'postgresql', 'redis', 'kafka', 'microservices', 'rest api',
            'graphql', 'machine learning', 'ai', 'data science', 'agile', 'scrum'
        ]

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract raw text from PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that don't add value
        text = re.sub(r'[•●▪▫■□◆◇○◉◊]', '', text)
        # Remove extra punctuation
        text = re.sub(r'\.{2,}', '', text)
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        return text.strip()

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
            'portfolio': None
        }

        # Extract email
        email_match = re.search(self.email_pattern, text, re.IGNORECASE)
        if email_match:
            contact_info['email'] = email_match.group(0)

        # Extract phone
        phone_match = re.search(self.phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)

        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(0)

        # Extract GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group(0)

        # Extract portfolio/website
        urls = re.findall(self.url_pattern, text)
        for url in urls:
            if 'linkedin' not in url.lower() and 'github' not in url.lower():
                contact_info['portfolio'] = url
                break

        return contact_info

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different resume sections"""
        sections = {}
        text_lower = text.lower()

        # Find all section headers and their positions
        section_positions = []
        for section_name, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                section_positions.append((match.start(), section_name, match.group(0)))

        # Sort by position
        section_positions.sort(key=lambda x: x[0])

        # Extract text between sections
        for i, (start, section_name, header) in enumerate(section_positions):
            # Get end position (start of next section or end of text)
            end = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)

            # Extract section content
            section_text = text[start:end].strip()

            # Store in sections dict (keep first occurrence of each section)
            if section_name not in sections:
                sections[section_name] = self.clean_text(section_text)

        return sections

    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = []

        # Look for common tech skills
        for skill in self.common_tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())

        # Also extract from skills section if exists
        skills_section_match = re.search(
            r'(?:skills?|technical skills?|competencies)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if skills_section_match:
            skills_text = skills_section_match.group(1)
            # Split by common delimiters
            additional_skills = re.split(r'[,|•●▪\n]', skills_text)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 2 and len(skill) < 50:
                    found_skills.append(skill)

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)

        return unique_skills

    def extract_experience_years(self, text: str) -> Optional[int]:
        """Estimate years of experience from resume"""
        # Look for explicit mentions
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience[:\s]+(\d+)\+?\s*years?'
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        # Try to estimate from work history dates
        date_pattern = r'(20\d{2}|19\d{2})'
        years = re.findall(date_pattern, text)
        if years:
            years = [int(y) for y in years]
            # Calculate range from oldest to newest
            return max(years) - min(years)

        return None

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []

        # Find education section
        education_match = re.search(
            r'(?:education|academic)[:\s]+(.*?)(?:\n\n[A-Z]|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if education_match:
            edu_text = education_match.group(1)

            # Look for degree patterns
            degree_patterns = [
                r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA)(?:\s+(?:of|in))?\s+([^,\n]+)',
                r'(Associate)(?:\s+(?:of|in))?\s+([^,\n]+)'
            ]

            for pattern in degree_patterns:
                matches = re.finditer(pattern, edu_text, re.IGNORECASE)
                for match in matches:
                    education.append({
                        'degree': match.group(0).strip(),
                        'field': match.group(2).strip() if len(match.groups()) > 1 else ''
                    })

        return education

    def parse(self, pdf_path: Path) -> Dict:
        """
        Main method to parse resume and return structured data

        Returns structured resume data with only essential information
        """
        # Extract raw text
        raw_text = self.extract_text_from_pdf(pdf_path)

        # Clean the text
        cleaned_text = self.clean_text(raw_text)

        # Extract structured data
        structured_data = {
            'contact_info': self.extract_contact_info(raw_text),
            'sections': self.extract_sections(raw_text),
            'skills': self.extract_skills(raw_text),
            'education': self.extract_education(raw_text),
            'estimated_experience_years': self.extract_experience_years(raw_text),
            'total_length': len(cleaned_text),
            'word_count': len(cleaned_text.split())
        }

        return structured_data

    def get_summary_for_analysis(self, structured_data: Dict, max_chars: int = 3000) -> str:
        """
        Create a concise summary of resume for API analysis
        Limits content to reduce token usage
        """
        summary_parts = []

        # Add contact info (minimal)
        if structured_data['contact_info']['email']:
            summary_parts.append(f"Email: {structured_data['contact_info']['email']}")

        # Add skills (most important for ATS)
        if structured_data['skills']:
            skills_str = ', '.join(structured_data['skills'][:20])  # Limit to top 20 skills
            summary_parts.append(f"\nSKILLS: {skills_str}")

        # Add experience section (truncated if needed)
        if 'experience' in structured_data['sections']:
            exp_text = structured_data['sections']['experience']
            if len(exp_text) > 1500:
                exp_text = exp_text[:1500] + "..."
            summary_parts.append(f"\nEXPERIENCE:\n{exp_text}")

        # Add education
        if structured_data['education']:
            edu_str = ' | '.join([edu['degree'] for edu in structured_data['education']])
            summary_parts.append(f"\nEDUCATION: {edu_str}")

        # Add summary/profile if exists
        if 'summary' in structured_data['sections']:
            summary_text = structured_data['sections']['summary']
            if len(summary_text) > 500:
                summary_text = summary_text[:500] + "..."
            summary_parts.append(f"\nPROFESSIONAL SUMMARY:\n{summary_text}")

        # Combine and limit total length
        full_summary = '\n'.join(summary_parts)

        if len(full_summary) > max_chars:
            full_summary = full_summary[:max_chars] + "\n...[Content truncated for brevity]"

        return full_summary

