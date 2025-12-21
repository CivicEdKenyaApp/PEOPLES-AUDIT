# generators/text_generator.py
import json
from typing import Dict, List, Any
from pathlib import Path
import logging

class TextGenerator:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self.load_data()
    
    def load_data(self):
        """Load all necessary data"""
        self.data = {}
        
        try:
            # Load consolidated data
            files_to_load = [
                'statistics_summary.json',
                'reform_agenda.json',
                'timeline_data.json',
                'constitutional_matrix.json',
                'charts_data.json'
            ]
            
            for filename in files_to_load:
                filepath = self.data_dir / filename
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.data[filename.replace('.json', '')] = json.load(f)
            
            self.logger.info("Data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
    
    def generate_all_documents(self) -> Dict[str, str]:
        """Generate all text documents"""
        documents = {}
        
        try:
            documents['citizen_summary'] = self.generate_citizen_summary()
            documents['executive_summary'] = self.generate_executive_summary()
            documents['action_handbook'] = self.generate_action_handbook()
            documents['constitutional_guide'] = self.generate_constitutional_guide()
            
            self.logger.info("All documents generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating documents: {str(e)}")
            raise
        
        return documents
    
    def generate_citizen_summary(self) -> str:
        """Generate citizen-friendly summary"""
        summary = """# Understanding Kenya's Economic Problems: A Citizen's Guide

## The Big Picture

Kenya is facing a serious economic crisis caused by corruption and bad governance. 
Here's what every Kenyan needs to know:

### 1. The Debt Crisis
Kenya's debt has grown from **KSh 2.4 trillion in 2014** to **KSh 12.05 trillion in 2025**. 
That's **5 times more debt** in just 11 years.

**What this means for you:**
- Every Kenyan – including newborn babies – owes **KSh 240,000** in public debt
- For every 100 shillings the government collects in taxes, **56 shillings** goes to paying debt
- Only **15 shillings** is left for building schools, hospitals, and roads

### 2. The Corruption Problem
Kenya loses about **KSh 800 billion every year** to corruption. That's like losing **one-third** of the national budget to thieves.

**Recent scandals:**
- **NYS Scandal:** KSh 9 billion stolen while youth waited for jobs
- **KEMSA COVID Scandal:** KSh 7.8 billion stolen while patients died without ventilators
- **Ghost Schools:** KSh 16.6 billion paid to 14 schools that don't exist
- **Maize Scandal (2009):** KSh 2 billion stolen during a drought

### 3. How This Affects Your Daily Life

**HUNGER**
- **15.5 million Kenyans** go hungry every day
- **20 million people** live below the poverty line
- Yet irrigation money meant for farmers is stolen

**JOBS**
- **13% of young Kenyans** are unemployed
- **1.7 million university graduates** cannot find work
- Youth programs like NYS and Kazi Kwa Vijana lost billions to corruption

**EDUCATION**
- 14 'ghost schools' received KSh 16.6 billion
- Real schools lack teachers, books, and desks
- University students can't get loans while politicians steal

**HEALTH**
- Hospitals lack medicine
- Government spends **KSh 17 million DAILY** on tea and snacks
- That daily snack money could insure **1 million Kenyans** for a year

### 4. Your Constitutional Rights Are Being Violated

The Constitution guarantees you:
- **Right to food** (Article 43) - but 15.5 million go hungry
- **Right to healthcare** (Article 43) - but hospitals lack medicine
- **Right to information** (Article 35) - but debt contracts are hidden
- **Right to protest** (Article 37) - but 200+ were killed in 2024 protests

### 5. What Needs to Change

**IMMEDIATE ACTIONS:**
1. **Publish all debt contracts** - let citizens see what we owe
2. **Stop the daily KSh 17 million** on government snacks
3. **Prosecute corruption cases** within 24 months, not 6 years
4. **Enforce the Election Campaign Financing Act** (it exists but has never been used)

**LONG-TERM REFORMS:**
1. **Transparency:** All government contracts online
2. **Accountability:** Jail politicians who steal
3. **Participation:** Citizens involved in budget decisions
4. **Justice:** Constitutional rights actually enforced

### 6. What You Can Do TODAY

1. **REQUEST INFORMATION:** Use Article 35 to ask for budget documents
2. **ATTEND BUDGET FORUMS:** Show up at county meetings
3. **REPORT CORRUPTION:** File complaints with EACC
4. **VOTE WISELY:** Reject candidates with corruption records
5. **ORGANIZE:** Join with others in your community

### Remember:
- **Article 1:** Sovereignty belongs to YOU
- **Article 10:** Government must act with integrity
- **Article 201:** Public money must be managed openly

This is your country. The Constitution is your contract. Demand that it be honored.

---
*Based on "THE-PEOPLES-AUDIT: From hustle to hardship" (December 8, 2025)*
*Generated by the People's Audit Pipeline*
"""
        
        return summary
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary"""
        stats = self.data.get('statistics_summary', {})
        
        summary = f"""# Executive Summary: People's Audit Analysis

## Key Findings

### 1. Fiscal Governance Crisis
- **Public Debt:** KSh {stats.get('total_debt', '12.05 trillion')} (2025)
- **Debt Service:** {stats.get('debt_service_ratio', '56%')} of revenue
- **Growth:** 500% increase since 2014 (KSh 2.4T to KSh 12.05T)
- **Per Capita Burden:** KSh 240,000 per Kenyan

### 2. Systemic Corruption
- **Annual Losses:** KSh {stats.get('corruption_loss_annual', '800 billion')}
- **Accountability Gap:** {stats.get('conviction_rate', '<10%')} conviction rate
- **Audit Compliance:** {stats.get('audit_implementation', '18%')} implementation rate
- **County Performance:** Only {stats.get('counties_clean_audit', '6/47')} counties with clean audits

### 3. Human Development Impact
- **Food Insecurity:** {stats.get('food_insecure', '15.5 million')} Kenyans
- **Youth Unemployment:** {stats.get('youth_unemployed', '1.7 million')} graduates
- **Service Delivery:** Critical failures in health, education, water sectors

### 4. Constitutional Violations
- **Articles Violated:** Multiple violations of Articles 1, 10, 35, 43, 201
- **Right to Information:** Systematic denial of access
- **Social Rights:** Failure to fulfill economic and social rights
- **Public Participation:** Tokenistic implementation

## Risk Assessment

### High Risk Areas:
1. **Debt Sustainability:** Approaching critical threshold
2. **Fiscal Space:** Severely constrained for development
3. **Social Stability:** Rising inequality and youth frustration
4. **Institutional Credibility:** Erosion of public trust

### Medium-Term Projections:
- Continued debt accumulation without corresponding development
- Escalating social tensions
- Further institutional degradation
- Reduced investment confidence

## Recommended Interventions

### Immediate (0-6 months):
1. **Debt Transparency Portal:** Publish all contracts
2. **Corruption Fast-Track Courts:** 24-month case resolution
3. **Supplementary Budget Controls:** Enforce 10% constitutional limit
4. **Ghost Project Audit:** Identify and recover stolen funds

### Short-Term (6-24 months):
1. **Political Finance Reform:** Enforce existing legislation
2. **Beneficial Ownership Registry:** Implement Companies Act Section 93A
3. **Audit Implementation Committee:** Cross-agency enforcement
4. **Citizen Oversight Mechanisms:** Institutionalize participation

### Structural (24+ months):
1. **Constitutional Amendments:** Ring-fence anti-corruption budgets
2. **Fiscal Responsibility Framework:** Binding debt ceilings
3. **Judicial Independence Guarantee:** Automatic funding allocation
4. **Devolution Enhancement:** County accountability mechanisms

## Implementation Considerations

### Political Economy:
- Resistance from vested interests expected
- Cross-party consensus needed for major reforms
- Civil society mobilization essential

### Resource Requirements:
- Minimal fiscal cost for transparency measures
- Reallocation from wasteful expenditure (e.g., KSh 6.2B annual snacks budget)
- Donor support available for governance reforms

### Success Indicators:
- Debt-to-GDP stabilization
- Corruption Perception Index improvement
- Audit implementation rate increase
- Public trust in institutions recovery

## Conclusion

Kenya faces a governance crisis requiring urgent, comprehensive reform. 
The solutions exist within current legal frameworks but require political will 
and citizen mobilization for implementation.

**Next Steps:**
1. Form multi-stakeholder reform implementation committee
2. Launch public awareness campaign
3. Initiate targeted legal actions
4. Establish monitoring and evaluation framework

---
*Analysis Period: 2014-2025*
*Data Sources: OAG, CoB, KNBS, Treasury, People's Audit*
*Generated: {self.get_current_date()}*
"""
        
        return summary
    
    def generate_action_handbook(self) -> str:
        """Generate citizen action handbook"""
        handbook = """# What Can I Do? A Citizen's Action Handbook

## Introduction

You have more power than you think. The Constitution gives you rights and tools to hold government accountable. This handbook shows you how to use them.

## PART 1: KNOW YOUR RIGHTS

### Key Constitutional Articles:

**Article 1:** Sovereignty belongs to the people
- **What it means:** All government power comes from you
- **How to use it:** Demand accountability from elected officials

**Article 35:** Right to information
- **What it means:** You can request any government document
- **How to use it:** Ask for budgets, contracts, reports

**Article 43:** Economic and social rights
- **What it means:** Rights to healthcare, food, education, housing
- **How to use it:** Demand these services in your community

**Article 201:** Principles of public finance
- **What it means:** Government money must be managed openly and fairly
- **How to use it:** Participate in budget processes

## PART 2: IMMEDIATE ACTIONS

### 1. Request Information (Article 35)

**Step-by-Step Guide:**

1. **Identify what you need:**
   - County budget documents
   - Project tender documents
   - Audit reports for your area
   - Debt contract details

2. **Find the right office:**
   - County government: County Secretary's office
   - National government: Relevant ministry's information officer
   - Parliament: Clerk's office

3. **Write your request:**

[Your Name]
[Your Address]
[Phone/Email]
[Date]

The Designated Information Officer
[Institution Name]
[Address]

RE: REQUEST FOR INFORMATION UNDER ARTICLE 35

Dear Sir/Madam,

Pursuant to Article 35 of the Constitution and the Access to Information Act 2016,
I request access to the following information:

[Be specific: e.g., "The complete tender document for Road Project X in my ward"]

[Add more items if needed]

This information is sought for purposes of public interest monitoring.

I request that this information be provided within 21 days as required by law.

Yours faithfully,

[Your Signature]
[Your Name]


4. **Submit and track:**
   - Submit via email (keep receipt)
   - Follow up after 14 days
   - If denied, appeal to Commission on Administrative Justice

### 2. Report Corruption

**Where to report:**

1. **EACC (Ethics and Anti-Corruption Commission)**
   - Online: portal.eacc.go.ke
   - Phone: 0800 22 22 33 (toll-free)
   - Offices: All 47 counties

2. **Office of the Auditor-General**
   - Report wasteful spending
   - Request special audits

3. **Controller of Budget**
   - Report budget violations
   - County expenditure concerns

**What you need:**
- Specific details (what, when, where, who)
- Documents if available
- Witnesses if possible

### 3. Participate in Budget Forums

**County Budget Process (March-May annually):**

1. **Get the documents:**
   - Request county budget estimates
   - Get development plan

2. **Prepare your input:**
   - Identify community priorities
   - Compare with actual needs
   - Prepare written submission

3. **Attend the forum:**
   - Register in advance
   - Speak clearly and briefly
   - Submit written version

4. **Follow up:**
   - Check if input was included
   - Monitor implementation

## PART 3: ORGANIZE COLLECTIVELY

### Form a Community Budget Committee

**Steps:**

1. **Gather interested neighbors** (10-20 people)
2. **Elect leaders:** Chair, Secretary, Treasurer
3. **Register with county** (optional but helpful)
4. **Monthly meetings** to:
   - Review county expenditure
   - Monitor local projects
   - Plan advocacy actions

### Join Existing Organizations

**National:**
- Okoa Uchumi Coalition
- Transparency International Kenya
- TISA (The Institute for Social Accountability)
- Katiba Institute

**County-level:**
- Check for local chapters
- Social justice centers
- Faith-based organizations
- Professional associations

## PART 4: USE THE COURTS

### Public Interest Litigation

**When to consider:**
- Government violates Constitution
- Rights of many people affected
- No other remedy available

**How to start:**

1. **Consult a lawyer** (many offer free initial consultations)
2. **Organizations that can help:**
   - Katiba Institute
   - ICJ-Kenya
   - Kituo Cha Sheria (free legal aid)

3. **Basic requirements:**
   - Clear violation of rights
   - Evidence of harm
   - Public interest affected

## PART 5: COUNTY-SPECIFIC ACTIONS

### For All 47 Counties:

**Monitor These Key Areas:**

1. **County Assembly:**
   - Attend sessions (they're public)
   - Read committee reports
   - Question your MCA

2. **County Executive:**
   - Track project implementation
   - Monitor service delivery
   - Report irregularities

3. **County Budget:**
   - 30% minimum for development
   - Check for inflated contracts
   - Monitor pending bills

## PART 6: DIGITAL TOOLS

### Websites to Bookmark:

1. **National Treasury:** treasury.go.ke (budgets, debt)
2. **Controller of Budget:** cob.go.ke (expenditure reports)
3. **Auditor-General:** oagkenya.go.ke (audit reports)
4. **Public Procurement:** suppliers.treasury.go.ke (tenders)
5. **EACC:** eacc.go.ke (corruption reports)

### Mobile Apps:
- **EACC ReportCorruption** (official app)
- **MyGov** (government services)
- **Ushahidi** (crowdsourcing platform)

## TEMPLATES AND SAMPLES

### Sample Information Request Letter

[Full template included in previous section]

### Sample Budget Submission

TO: COUNTY BUDGET AND APPROPRIATIONS COMMITTEE
FROM: [YOUR COMMUNITY GROUP]
DATE: [DATE]
SUBJECT: INPUT ON FY 2024/25 BUDGET

Our community priorities are:

Clean water connection for 500 households

Repair of [Road Name]

Additional teachers for [School Name]

Current gaps:

No budget for water project despite promises

Road repair funds insufficient

School understaffed despite capitation

Our recommendations:

Allocate KSh [amount] for water project

Increase road repair budget by KSh [amount]

Hire 3 more teachers for [School Name]

Attached: Signed petition from 300 residents


### Sample EACC Complaint

[Download from eacc.go.ke]

## SAFETY TIPS

### When Documenting Corruption:

1. **Be discreet** - don't confront suspects directly
2. **Use phone camera** safely
3. **Keep copies** of all documents
4. **Share information** with trusted organizations
5. **Use anonymous reporting** if concerned about safety

### At Protests:

1. **Know your rights** (Article 37: peaceful assembly)
2. **Notify police** 3 days in advance
3. **Stay peaceful**
4. **Document police conduct**
5. **Have emergency contacts** ready

## SUCCESS STORIES

### Example 1: Makueni County
- Citizens tracked water project funds
- Exposed inflated contracting
- Recovered KSh 50 million
- Project completed at actual cost

### Example 2: Nairobi Community
- Used Article 35 to request road tender documents
- Found contractor had no capacity
- Stopped KSh 200 million wasteful project
- Proper bidding conducted

## REMEMBER

You are not powerless. The Constitution gives you tools. 
Corruption thrives in darkness - shine light on it.

**Start today:**
1. Pick one action from this handbook
2. Do it this week
3. Share with three friends
4. Build momentum

---
*This handbook is based on the People's Audit analysis*
*For updates and resources: [Contact Okoa Uchumi Coalition]*
"""
        
        return handbook
    
    def generate_constitutional_guide(self) -> str:
        """Generate constitutional rights guide"""
        constitutional_data = self.data.get('constitutional_matrix', {})
        
        guide = """# Your Rights Under the Constitution

## Introduction

The Constitution of Kenya (2010) is the supreme law of the land. 
It's your contract with the government. This guide explains your key rights 
and how they're being violated according to the People's Audit.

## How to Use This Guide

1. **Look up specific articles** mentioned in news or reports
2. **Understand what each right means** in simple language
3. **See evidence of violations** from the audit
4. **Learn how to enforce** your rights

## Key Rights and Violations

"""

        # Add articles with violations
        if constitutional_data:
            for article_num, article_data in constitutional_data.items():
                if article_data.get('violation_count', 0) > 0:
                    guide += f"\n### Article {article_num}\n\n"
                    
                    # Add simple explanation
                    explanation = self.get_article_explanation(article_num)
                    guide += f"**What it means:** {explanation}\n\n"
                    
                    # Add violation examples
                    violations = article_data.get('violations', [])
                    if violations:
                        guide += "**How it's being violated:**\n"
                        for i, violation in enumerate(violations[:2], 1):
                            guide += f"{i}. {violation.get('text', '')[:150]}...\n"
                        guide += "\n"
                    
                    guide += f"**Violations found:** {article_data.get('violation_count', 0)}\n"
                    guide += "-" * 40 + "\n"
        
        guide += """

## How to Enforce Your Rights

### Step 1: Document the Violation
- Write down what happened, when, where
- Take photos if safe and relevant
- Gather supporting documents
- Get witness statements

### Step 2: Choose the Right Avenue

**For information denial:**
- Appeal to Commission on Administrative Justice (CAJ)
- Contact: caj.go.ke, 0800 221 111

**For corruption:**
- Report to EACC: portal.eacc.go.ke, 0800 22 22 33
- Provide specific evidence

**For budget violations:**
- Contact Controller of Budget: cob.go.ke
- Report to your MP and Senator

**For human rights violations:**
- Kenya National Commission on Human Rights (KNCHR)
- Contact: knchr.org, 0800 720 627

### Step 3: Escalate if Needed

**Legal Options:**
1. **Public Interest Litigation:** File case in High Court
2. **Constitutional Petition:** Challenge unconstitutional actions
3. **Judicial Review:** Review government decisions

**Organizations that can help:**
- Katiba Institute: katibainstitute.org
- ICJ-Kenya: icj-kenya.org
- Kituo Cha Sheria: kituochasheria.or.ke (free legal aid)

## Your Power as a Citizen

**Remember:**
- Article 1: Sovereignty belongs to YOU
- Article 10: Government must serve YOU
- Article 201: Your taxes must benefit YOU

**Take Action Today:**
1. Pick one right being violated in your community
2. Use the templates in this guide
3. Start with an information request
4. Build evidence
5. Mobilize others

## Resources

**Online:**
- Full Constitution: kenyalaw.org
- Court cases: kenyalaw.org/caselaw
- Government reports: treasury.go.ke

**Hotlines:**
- EACC: 0800 22 22 33
- KNCHR: 0800 720 627
- CAJ: 0800 221 111

**Mobile Apps:**
- EACC ReportCorruption
- MyGov Kenya

---
*Based on analysis of constitutional violations in the People's Audit*
*Generated for citizen empowerment and accountability*
"""
        
        return guide
    
    def get_article_explanation(self, article_num: str) -> str:
        """Get simple explanation of article"""
        explanations = {
            '1': "All sovereign power belongs to the people of Kenya. Government gets its authority from the people.",
            '10': "Lists national values: patriotism, unity, rule of law, democracy, human dignity, equity, good governance.",
            '35': "Right to access information held by the state. Government must give you information when you ask.",
            '43': "Economic and social rights: healthcare, food, water, housing, education, social security.",
            '73': "Leadership and integrity. Authority is a public trust to be exercised for the people's benefit.",
            '201': "Principles of public finance: openness, accountability, public participation, equitable sharing.",
            '229': "Values and principles of public service: high standards, professionalism, efficiency."
        }
        
        # Clean article number
        clean_num = ''.join(filter(str.isdigit, article_num))
        return explanations.get(clean_num, f"Article {article_num} of the Constitution")
    
    def get_current_date(self) -> str:
        """Get current date"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")