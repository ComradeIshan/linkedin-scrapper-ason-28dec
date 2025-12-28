"""
LinkedIn Profile Analyzer with Gemini AI Integration
WARNING: This is for educational purposes only. 
LinkedIn's ToS prohibits automated scraping.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

class LinkedInProfileAnalyzer:
    def __init__(self, email, password, gemini_api_key):
        self.email = email
        self.password = password
        self.driver = None
        self.wait = None
        
        # Configure Gemini AI
        try:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✓ Gemini AI configured successfully")
        except Exception as e:
            print(f"✗ Error configuring Gemini: {e}")
            raise
        
    def setup_driver(self):
        """Initialize Chrome driver with options"""
        print("\n[1/6] Setting up Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✓ Chrome driver ready")
        
    def login(self):
        """Login to LinkedIn"""
        print("\n[2/6] Logging into LinkedIn...")
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(3)
        
        try:
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            print("✓ Email entered")
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            print("✓ Password entered")
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(7)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "feed" in current_url or "mynetwork" in current_url:
                print("✓ Login successful!")
                return True
            elif "challenge" in current_url or "checkpoint" in current_url:
                print("⚠ CAPTCHA or security challenge detected!")
                print("Please solve it manually in the browser window...")
                input("Press Enter after solving the challenge...")
                return True
            else:
                print(f"⚠ Unexpected redirect: {current_url}")
                print("Login may have failed. Check credentials.")
                return False
            
        except Exception as e:
            print(f"✗ Login failed: {e}")
            self.driver.save_screenshot("login_error.png")
            print("Screenshot saved as login_error.png")
            raise
            
    def search_profile(self, target_username):
        """Search for target user profile"""
        print(f"\n[3/6] Navigating to profile: {target_username}")
        
        # Navigate to profile
        profile_url = f"https://www.linkedin.com/in/{target_username}/"
        self.driver.get(profile_url)
        print(f"✓ Opened: {profile_url}")
        
        # Wait for page load
        time.sleep(5)
        
        # Check if profile exists
        if "Page not found" in self.driver.page_source or "404" in self.driver.title:
            print("✗ Profile not found! Check the username.")
            return False
            
        print("✓ Profile page loaded")
        
        # Scroll down to load more content
        print("Scrolling to load all sections...")
        for i in range(3):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/{3-i});")
            time.sleep(2)
        
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        print("✓ Page fully loaded")
        return True
        
    def scrape_profile_data(self):
        """Scrape all relevant data from the profile"""
        print("\n[4/6] Scraping profile data...")
        profile_data = {}
        
        # Take screenshot for debugging
        self.driver.save_screenshot("profile_page.png")
        print("✓ Screenshot saved as profile_page.png")
        
        try:
            # Name - Try multiple selectors
            try:
                name_selectors = [
                    "h1.text-heading-xlarge",
                    "h1.inline.t-24.v-align-middle.break-words",
                    "h1[class*='heading']",
                    "div.ph5 h1"
                ]
                
                name = None
                for selector in name_selectors:
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name = name_element.text.strip()
                        if name:
                            break
                    except:
                        continue
                
                profile_data['name'] = name if name else "Not found"
                print(f"  ✓ Name: {profile_data['name']}")
            except Exception as e:
                profile_data['name'] = "Not found"
                print(f"  ✗ Name: {e}")
            
            # Headline
            try:
                headline_selectors = [
                    "div.text-body-medium.break-words",
                    "div.pv-text-details__left-panel div.text-body-medium",
                    "div[class*='headline']"
                ]
                
                headline = None
                for selector in headline_selectors:
                    try:
                        headline_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        headline = headline_element.text.strip()
                        if headline and len(headline) > 5:
                            break
                    except:
                        continue
                
                profile_data['headline'] = headline if headline else "Not found"
                print(f"  ✓ Headline: {profile_data['headline'][:50]}...")
            except Exception as e:
                profile_data['headline'] = "Not found"
                print(f"  ✗ Headline: {e}")
            
            # Location
            try:
                location_selectors = [
                    "span.text-body-small.inline.t-black--light.break-words",
                    "div.pv-text-details__left-panel span.text-body-small",
                    "span[class*='location']"
                ]
                
                location = None
                for selector in location_selectors:
                    try:
                        location_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        location = location_element.text.strip()
                        if location:
                            break
                    except:
                        continue
                
                profile_data['location'] = location if location else "Not found"
                print(f"  ✓ Location: {profile_data['location']}")
            except Exception as e:
                profile_data['location'] = "Not found"
                print(f"  ✗ Location: {e}")
            
            # About section
            try:
                # Click "Show more" if present
                try:
                    show_more = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Show more']")
                    self.driver.execute_script("arguments[0].click();", show_more)
                    time.sleep(1)
                except:
                    pass
                
                about_selectors = [
                    "section[data-section='summary'] div.display-flex.ph5.pv3",
                    "div.pv-about-section div.pv-about__summary-text",
                    "section.artdeco-card.pv-about-section div.display-flex"
                ]
                
                about = None
                for selector in about_selectors:
                    try:
                        about_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        about = about_element.text.strip()
                        if about and len(about) > 10:
                            break
                    except:
                        continue
                
                if not about:
                    # Try finding by section ID
                    try:
                        about_section = self.driver.find_element(By.XPATH, "//section[contains(@id, 'about')]")
                        about = about_section.text.strip()
                    except:
                        pass
                
                profile_data['about'] = about if about else "Not found"
                print(f"  ✓ About: {len(profile_data['about'])} characters")
            except Exception as e:
                profile_data['about'] = "Not found"
                print(f"  ✗ About: {e}")
            
            # Experience
            try:
                experience_selectors = [
                    "section[data-section='experience'] ul li",
                    "div#experience ~ div ul.pvs-list li",
                    "section.artdeco-card.pv-profile-card ul li"
                ]
                
                experiences = []
                for selector in experience_selectors:
                    try:
                        exp_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if exp_elements:
                            experiences = exp_elements
                            break
                    except:
                        continue
                
                profile_data['experience'] = []
                for exp in experiences[:5]:
                    try:
                        exp_text = exp.text.strip()
                        if exp_text and len(exp_text) > 10:
                            profile_data['experience'].append(exp_text)
                    except:
                        continue
                
                print(f"  ✓ Experience: {len(profile_data['experience'])} entries")
            except Exception as e:
                profile_data['experience'] = []
                print(f"  ✗ Experience: {e}")
            
            # Education
            try:
                education_selectors = [
                    "section[data-section='education'] ul li",
                    "div#education ~ div ul.pvs-list li",
                    "section.pv-profile-section.education-section ul li"
                ]
                
                educations = []
                for selector in education_selectors:
                    try:
                        edu_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if edu_elements:
                            educations = edu_elements
                            break
                    except:
                        continue
                
                profile_data['education'] = []
                for edu in educations[:3]:
                    try:
                        edu_text = edu.text.strip()
                        if edu_text and len(edu_text) > 10:
                            profile_data['education'].append(edu_text)
                    except:
                        continue
                
                print(f"  ✓ Education: {len(profile_data['education'])} entries")
            except Exception as e:
                profile_data['education'] = []
                print(f"  ✗ Education: {e}")
            
            # Skills
            try:
                # Try to navigate to skills section
                try:
                    skills_button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/details/skills')]")
                    self.driver.execute_script("arguments[0].scrollIntoView();", skills_button)
                    time.sleep(1)
                except:
                    pass
                
                skill_selectors = [
                    "div.pvs-list__container span[aria-hidden='true']",
                    "section[data-section='skills'] span",
                    "div.pv-skill-category-entity__name span"
                ]
                
                skills = []
                for selector in skill_selectors:
                    try:
                        skill_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        skills = [s.text.strip() for s in skill_elements if s.text.strip()]
                        if skills:
                            break
                    except:
                        continue
                
                # Remove duplicates and limit
                profile_data['skills'] = list(set(skills))[:15]
                print(f"  ✓ Skills: {len(profile_data['skills'])} found")
            except Exception as e:
                profile_data['skills'] = []
                print(f"  ✗ Skills: {e}")
            
            print("\n✓ Profile data scraping complete!")
            
            # Print summary
            print("\n--- SCRAPED DATA SUMMARY ---")
            print(f"Name: {profile_data.get('name', 'N/A')}")
            print(f"Headline: {profile_data.get('headline', 'N/A')[:60]}...")
            print(f"About: {len(profile_data.get('about', ''))} chars")
            print(f"Experience: {len(profile_data.get('experience', []))} entries")
            print(f"Education: {len(profile_data.get('education', []))} entries")
            print(f"Skills: {len(profile_data.get('skills', []))} items")
            print("----------------------------\n")
            
            return profile_data
            
        except Exception as e:
            print(f"✗ Error scraping profile: {e}")
            return profile_data
    
    def analyze_with_gemini(self, profile_data):
        """Analyze profile data using Gemini AI"""
        print("[5/6] Analyzing profile with Gemini AI...")
        
        # Check if we have enough data
        if profile_data.get('name') == "Not found":
            print("✗ Insufficient data for analysis")
            return "Analysis failed: Profile data could not be scraped properly. Please check the username and try again."
        
        # Create prompt for Gemini
        prompt = f"""
        You are a professional LinkedIn profile consultant. Analyze the following LinkedIn profile and provide a comprehensive assessment.
        
        PROFILE DATA:
        =============
        Name: {profile_data.get('name', 'N/A')}
        Headline: {profile_data.get('headline', 'N/A')}
        Location: {profile_data.get('location', 'N/A')}
        
        ABOUT SECTION:
        {profile_data.get('about', 'Not provided')}
        
        EXPERIENCE:
        {chr(10).join(f"{i+1}. {exp}" for i, exp in enumerate(profile_data.get('experience', []))) if profile_data.get('experience') else 'No experience data available'}
        
        EDUCATION:
        {chr(10).join(f"{i+1}. {edu}" for i, edu in enumerate(profile_data.get('education', []))) if profile_data.get('education') else 'No education data available'}
        
        SKILLS:
        {', '.join(profile_data.get('skills', [])) if profile_data.get('skills') else 'No skills listed'}
        
        ANALYSIS REQUIRED:
        ==================
        1. OVERALL RATING: Rate this profile from 1-10 based on completeness, professionalism, and impact
        
        2. PROFILE STRENGTHS: Identify 3-5 strong points about this profile
        
        3. AREAS FOR IMPROVEMENT: List specific sections that need enhancement
        
        4. DETAILED RECOMMENDATIONS:
           - Headline optimization suggestions
           - About section improvements
           - Experience section tips
           - Skills recommendations
           - Overall profile enhancement strategies
        
        5. CONTENT STRATEGY: Suggest types of posts and content this person should share
        
        6. COMPETITIVE POSITIONING: How this profile stands compared to industry standards
        
        Please provide actionable, specific feedback that can be immediately implemented.
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = response.text
            print("✓ Analysis complete!")
            return analysis
            
        except Exception as e:
            print(f"✗ Error with Gemini analysis: {e}")
            return f"Analysis failed: {str(e)}"
    
    def generate_pdf_report(self, profile_data, analysis):
        """Generate PDF report with profile data and analysis"""
        print("\n[6/6] Generating PDF report...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = profile_data.get('name', 'profile').replace(' ', '_').replace('/', '_')
        filename = f"linkedin_analysis_{safe_name}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                                leftMargin=0.75*inch, rightMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#0077B5',
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#0077B5',
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("LinkedIn Profile Analysis Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              ParagraphStyle('subtitle', parent=styles['Normal'], alignment=1, fontSize=10)))
        story.append(Spacer(1, 0.3*inch))
        
        # Profile Data Section
        story.append(Paragraph("📊 Profile Information", heading_style))
        story.append(Paragraph(f"<b>Name:</b> {profile_data.get('name', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Headline:</b> {profile_data.get('headline', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Location:</b> {profile_data.get('location', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # About Section
        if profile_data.get('about') and profile_data['about'] != "Not found":
            story.append(Paragraph("📝 About", heading_style))
            story.append(Paragraph(profile_data.get('about', 'N/A'), styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Experience
        if profile_data.get('experience'):
            story.append(Paragraph("💼 Experience", heading_style))
            for i, exp in enumerate(profile_data.get('experience', []), 1):
                story.append(Paragraph(f"<b>{i}.</b> {exp}", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
        
        # Education
        if profile_data.get('education'):
            story.append(Paragraph("🎓 Education", heading_style))
            for i, edu in enumerate(profile_data.get('education', []), 1):
                story.append(Paragraph(f"<b>{i}.</b> {edu}", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
        
        # Skills
        if profile_data.get('skills'):
            story.append(Paragraph("⚡ Skills", heading_style))
            story.append(Paragraph(', '.join(profile_data.get('skills', [])), styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Page break before analysis
        story.append(PageBreak())
        
        # AI Analysis
        story.append(Paragraph("🤖 AI-Powered Profile Analysis & Recommendations", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Split analysis into paragraphs and format
        analysis_lines = analysis.split('\n')
        for line in analysis_lines:
            line = line.strip()
            if line:
                # Check if it's a heading (contains numbers or special markers)
                if any(marker in line for marker in ['1.', '2.', '3.', '4.', '5.', '6.', 'RATING:', 'STRENGTHS:', 'IMPROVEMENT:']):
                    story.append(Paragraph(f"<b>{line}</b>", styles['Heading3']))
                else:
                    story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        try:
            doc.build(story)
            print(f"✓ PDF report generated: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Error generating PDF: {e}")
            return None
    
    def run_analysis(self, target_username):
        """Main method to run complete analysis"""
        print("\n" + "="*60)
        print("  LINKEDIN PROFILE ANALYZER WITH GEMINI AI")
        print("="*60)
        
        try:
            # Setup and login
            self.setup_driver()
            
            if not self.login():
                print("\n✗ Login failed. Please check your credentials.")
                return None
            
            # Search and scrape profile
            if not self.search_profile(target_username):
                print("\n✗ Could not load profile. Please verify the username.")
                return None
                
            profile_data = self.scrape_profile_data()
            
            # Check if we got meaningful data
            if profile_data.get('name') == "Not found":
                print("\n✗ Failed to scrape profile data. Possible reasons:")
                print("  - Profile may be private")
                print("  - Username may be incorrect")
                print("  - LinkedIn may have changed its layout")
                print("  - CAPTCHA or verification required")
                return None
            
            # Analyze with Gemini
            analysis = self.analyze_with_gemini(profile_data)
            
            # Generate PDF report
            pdf_filename = self.generate_pdf_report(profile_data, analysis)
            
            # Final summary
            print("\n" + "="*60)
            print("  ✓ ANALYSIS COMPLETE!")
            print("="*60)
            print(f"\n📌 Profile: {profile_data.get('name', 'Unknown')}")
            print(f"📄 Report: {pdf_filename}")
            print(f"\n{analysis}")
            print("\n" + "="*60)
            
            return profile_data, analysis, pdf_filename
            
        except KeyboardInterrupt:
            print("\n\n⚠ Analysis interrupted by user")
            
        except Exception as e:
            print(f"\n✗ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()
                print("✓ Browser closed")

# ========================================
# CONFIGURATION - CHANGE THESE VALUES
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LinkedIn Profile Analyzer Configuration")
    print("="*60 + "\n")
    
    # METHOD 1: Enter credentials here directly
    LINKEDIN_EMAIL = "aliayaan1719@gmail.com"      # ← Your LinkedIn email
    LINKEDIN_PASSWORD = "Red#label_187"             # ← Your LinkedIn password
    GEMINI_API_KEY = ""         # ← Your Gemini API key
    TARGET_USERNAME = "reva-nimgaonkar"             # ← Target's LinkedIn username             important, you can change according to your need
    
    # METHOD 2: Or enter them interactively (uncomment below)
    # LINKEDIN_EMAIL = input("Enter your LinkedIn email: ")
    # LINKEDIN_PASSWORD = input("Enter your LinkedIn password: ")
    # GEMINI_API_KEY = input("Enter your Gemini API key: ")
    # TARGET_USERNAME = input("Enter target LinkedIn username: ")
    
    # Validate inputs
    if "your_email" in LINKEDIN_EMAIL or "your_password" in LINKEDIN_PASSWORD:
        print("⚠ Please update the credentials in the code!")
        print("Edit lines 555-558 with your actual values.\n")
        exit(1)
    
    print(f"Target Profile: linkedin.com/in/{TARGET_USERNAME}")
    print("\nStarting analysis...\n")
    
    # Run analyzer
    analyzer = LinkedInProfileAnalyzer(LINKEDIN_EMAIL, LINKEDIN_PASSWORD, GEMINI_API_KEY)

    analyzer.run_analysis(TARGET_USERNAME)
