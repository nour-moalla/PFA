"""Tests for resume parser module"""
import pytest
import re
from app.core.resume_parser import ResumeParser


def test_resume_parser_initialization():
    """Test that ResumeParser initializes correctly"""
    parser = ResumeParser()
    
    assert parser is not None
    assert hasattr(parser, 'section_patterns')
    assert hasattr(parser, 'email_pattern')
    assert hasattr(parser, 'phone_pattern')
    assert hasattr(parser, 'common_tech_skills')


def test_resume_parser_section_patterns():
    """Test that section patterns are defined"""
    parser = ResumeParser()
    
    # Check key sections exist
    assert 'contact' in parser.section_patterns
    assert 'summary' in parser.section_patterns
    assert 'experience' in parser.section_patterns
    assert 'education' in parser.section_patterns
    assert 'skills' in parser.section_patterns
    
    # Verify patterns are regex strings
    for section, pattern in parser.section_patterns.items():
        assert isinstance(pattern, str)
        # Verify they compile as valid regex
        compiled = re.compile(pattern, re.IGNORECASE)
        assert compiled is not None


def test_email_pattern_matches_valid_emails():
    """Test that email pattern matches valid email addresses"""
    parser = ResumeParser()
    
    valid_emails = [
        'john.doe@example.com',
        'user+tag@domain.co.uk',
        'test.email123@company-name.org',
    ]
    
    for email in valid_emails:
        match = re.search(parser.email_pattern, email)
        assert match is not None, f"Pattern should match {email}"


def test_email_pattern_rejects_invalid_emails():
    """Test that email pattern doesn't match invalid emails"""
    parser = ResumeParser()
    
    invalid_emails = [
        'not-an-email',
        '@domain.com',
        'name@',
    ]
    
    for email in invalid_emails:
        match = re.search(parser.email_pattern, email)
        assert match is None, f"Pattern should not match {email}"


def test_phone_pattern_matches_valid_phones():
    """Test that phone pattern matches various phone formats"""
    parser = ResumeParser()
    
    valid_phones = [
        '(555) 123-4567',
        '555-123-4567',
        '+1 555 123 4567',
        '5551234567',
    ]
    
    for phone in valid_phones:
        match = re.search(parser.phone_pattern, phone)
        assert match is not None, f"Pattern should match {phone}"


def test_url_pattern_matches_valid_urls():
    """Test that URL pattern matches valid URLs"""
    parser = ResumeParser()
    
    valid_urls = [
        'https://www.example.com',
        'http://github.com/user/repo',
        'https://linkedin.com/in/johnsmith',
    ]
    
    for url in valid_urls:
        match = re.search(parser.url_pattern, url)
        assert match is not None, f"Pattern should match {url}"


def test_common_tech_skills_populated():
    """Test that common tech skills list is populated"""
    parser = ResumeParser()
    
    assert len(parser.common_tech_skills) > 0
    assert 'python' in parser.common_tech_skills
    assert 'javascript' in parser.common_tech_skills
    assert 'docker' in parser.common_tech_skills
    
    # Verify all skills are lowercase for case-insensitive matching
    for skill in parser.common_tech_skills:
        assert skill == skill.lower(), f"Skill '{skill}' should be lowercase"


def test_resume_parser_has_required_methods():
    """Test that ResumeParser has all required methods"""
    parser = ResumeParser()
    
    required_methods = ['parse', 'extract_text_from_pdf']
    for method in required_methods:
        assert hasattr(parser, method), f"ResumeParser should have {method} method"
        assert callable(getattr(parser, method)), f"{method} should be callable"
