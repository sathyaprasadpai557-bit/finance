"""
AI Personal Finance & Expense Coach - Python Backend
====================================================
Complete backend implementation with Flask API integration
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict
import statistics


# =====================================================
# CORE CLASSES
# =====================================================

class ExpenseCategorizationEngine:
    """AI-powered expense categorization using keyword matching."""
    
    CATEGORY_KEYWORDS = {
        'food': ['coffee', 'lunch', 'dinner', 'breakfast', 'restaurant', 
                 'food', 'pizza', 'burger', 'meal', 'cafe', 'bistro'],
        'transport': ['uber', 'taxi', 'gas', 'fuel', 'parking', 'transit', 
                      'bus', 'train', 'lyft', 'metro', 'subway'],
        'entertainment': ['movie', 'netflix', 'spotify', 'game', 'concert', 
                         'show', 'theatre', 'cinema', 'streaming'],
        'shopping': ['amazon', 'clothing', 'shoes', 'store', 'mall', 
                    'shop', 'boutique', 'ebay'],
        'utilities': ['electric', 'water', 'internet', 'phone', 'bill', 
                     'utility', 'cable', 'wifi'],
        'health': ['pharmacy', 'doctor', 'gym', 'fitness', 'medicine', 
                  'hospital', 'clinic', 'wellness'],
        'groceries': ['grocery', 'supermarket', 'market', 'vegetables', 
                     'fruits', 'whole foods', 'trader joes', 'safeway']
    }
    
    @classmethod
    def categorize(cls, description: str) -> str:
        """Categorize an expense based on its description."""
        description_lower = description.lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'other'


class Expense:
    """Represents a single expense transaction."""
    
    def __init__(self, description: str, amount: float, 
                 date: str = None, category: str = None):
        self.description = description
        self.amount = amount
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.category = category or ExpenseCategorizationEngine.categorize(description)
        self.id = hash(f"{description}{amount}{self.date}")
    
    def to_dict(self) -> Dict:
        """Convert expense to dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        """Create expense from dictionary."""
        return cls(
            description=data['description'],
            amount=data['amount'],
            date=data.get('date'),
            category=data.get('category')
        )
    
    def __repr__(self):
        return f"Expense('{self.description}', ${self.amount:.2f}, {self.category})"


class NaturalLanguageParser:
    """Parse natural language expense input."""
    
    @staticmethod
    def parse_expense_text(text: str) -> List[Expense]:
        """Parse natural language text into expense objects."""
        expenses = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            # Match dollar amounts: $5.50 or 5.50
            amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', line)
            
            if amount_match:
                amount = float(amount_match.group(1))
                description = re.sub(r'\$?\d+(?:\.\d{2})?', '', line).strip()
                
                if description:
                    expenses.append(Expense(description, amount))
        
        return expenses


class SpendingAnalyzer:
    """Analyze spending patterns and generate insights."""
    
    def __init__(self, expenses: List[Expense]):
        self.expenses = expenses
    
    def get_total_spending(self) -> float:
        """Calculate total spending."""
        return sum(exp.amount for exp in self.expenses)
    
    def get_average_transaction(self) -> float:
        """Calculate average transaction amount."""
        if not self.expenses:
            return 0.0
        return self.get_total_spending() / len(self.expenses)
    
    def get_category_totals(self) -> Dict[str, float]:
        """Get spending totals by category."""
        totals = defaultdict(float)
        for exp in self.expenses:
            totals[exp.category] += exp.amount
        return dict(totals)
    
    def get_top_category(self) -> Tuple[str, float]:
        """Get the category with highest spending."""
        totals = self.get_category_totals()
        if not totals:
            return ('none', 0.0)
        return max(totals.items(), key=lambda x: x[1])
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Expense]:
        """Detect unusual spending patterns."""
        if len(self.expenses) < 2:
            return []
        
        avg = self.get_average_transaction()
        anomalies = [exp for exp in self.expenses if exp.amount > avg * threshold]
        
        return sorted(anomalies, key=lambda x: x.amount, reverse=True)
    
    def get_spending_by_date(self) -> Dict[str, float]:
        """Get daily spending totals."""
        daily = defaultdict(float)
        for exp in self.expenses:
            daily[exp.date] += exp.amount
        return dict(sorted(daily.items()))
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive spending statistics."""
        if not self.expenses:
            return {
                'total': 0,
                'average': 0,
                'median': 0,
                'std_dev': 0,
                'count': 0,
                'min': 0,
                'max': 0
            }
        
        amounts = [exp.amount for exp in self.expenses]
        
        return {
            'total': sum(amounts),
            'average': statistics.mean(amounts),
            'median': statistics.median(amounts),
            'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
            'count': len(amounts),
            'min': min(amounts),
            'max': max(amounts)
        }


class FinancialAdvisor:
    """Generate personalized financial advice."""
    
    def __init__(self, analyzer: SpendingAnalyzer):
        self.analyzer = analyzer
    
    def generate_advice(self) -> List[str]:
        """Generate personalized savings advice."""
        advice = []
        
        if not self.analyzer.expenses:
            return ["Start tracking your expenses to get personalized advice!"]
        
        total = self.analyzer.get_total_spending()
        category_totals = self.analyzer.get_category_totals()
        top_category, top_amount = self.analyzer.get_top_category()
        
        # Advice for dominant category
        if top_amount > total * 0.4:
            percentage = int((top_amount / total) * 100)
            advice.append(
                f"💡 Your {top_category} spending is {percentage}% of your total expenses. "
                f"Consider setting a monthly budget limit of ${top_amount * 0.85:.2f} "
                f"to reduce this by 15%."
            )
        
        # Food-specific advice
        if 'food' in category_totals and category_totals['food'] > total * 0.3:
            food_spending = category_totals['food']
            advice.append(
                f"🍽️ Food expenses are high at ${food_spending:.2f}. "
                f"Meal prepping 3-4 days a week could save you approximately "
                f"${food_spending * 0.3:.2f} per week!"
            )
        
        # Transport advice
        if 'transport' in category_totals and category_totals['transport'] > total * 0.25:
            transport = category_totals['transport']
            advice.append(
                f"🚗 Transportation costs are ${transport:.2f}. "
                f"Consider carpooling or public transit to save up to "
                f"${transport * 0.4:.2f} monthly."
            )
        
        # Savings goal
        savings_potential = top_amount * 0.15
        advice.append(
            f"💰 Weekly savings goal: Try to reduce your {top_category} spending "
            f"by 15% to save ${savings_potential:.2f}. Small changes add up!"
        )
        
        # Entertainment advice
        if 'entertainment' in category_totals:
            ent = category_totals['entertainment']
            if ent > total * 0.2:
                advice.append(
                    f"🎬 Entertainment spending is ${ent:.2f}. "
                    f"Look for free community events or share streaming subscriptions."
                )
        
        return advice
    
    def generate_weekly_report(self) -> Dict:
        """Generate a comprehensive weekly report."""
        stats = self.analyzer.calculate_statistics()
        anomalies = self.analyzer.detect_anomalies()
        advice = self.generate_advice()
        
        return {
            'statistics': stats,
            'category_breakdown': self.analyzer.get_category_totals(),
            'top_category': self.analyzer.get_top_category()[0],
            'anomalies': [exp.to_dict() for exp in anomalies],
            'advice': advice,
            'daily_spending': self.analyzer.get_spending_by_date()
        }


class ExpenseManager:
    """Main class to manage all expense operations."""
    
    def __init__(self):
        self.expenses: List[Expense] = []
    
    def add_expense(self, description: str, amount: float, 
                   date: str = None, category: str = None) -> Expense:
        """Add a single expense."""
        expense = Expense(description, amount, date, category)
        self.expenses.append(expense)
        return expense
    
    def add_expenses_from_text(self, text: str) -> List[Expense]:
        """Parse and add expenses from natural language text."""
        parser = NaturalLanguageParser()
        new_expenses = parser.parse_expense_text(text)
        self.expenses.extend(new_expenses)
        return new_expenses
    
    def get_analyzer(self) -> SpendingAnalyzer:
        """Get analyzer for current expenses."""
        return SpendingAnalyzer(self.expenses)
    
    def get_advisor(self) -> FinancialAdvisor:
        """Get financial advisor."""
        return FinancialAdvisor(self.get_analyzer())
    
    def export_to_json(self, filename: str = 'expenses.json'):
        """Export expenses to JSON file."""
        data = [exp.to_dict() for exp in self.expenses]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported {len(data)} expenses to {filename}")
    
    def import_from_json(self, filename: str = 'expenses.json'):
        """Import expenses from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.expenses = [Expense.from_dict(exp) for exp in data]
            print(f"✅ Imported {len(self.expenses)} expenses from {filename}")
        except FileNotFoundError:
            print(f"❌ File {filename} not found.")


# =====================================================
# FLASK API (Optional - for web integration)
# =====================================================

def create_flask_app():
    """Create Flask API for web integration."""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        manager = ExpenseManager()
        
        @app.route('/api/expenses', methods=['POST'])
        def add_expense():
            """Add a new expense."""
            data = request.json
            expense = manager.add_expense(
                description=data['description'],
                amount=float(data['amount']),
                date=data.get('date'),
                category=data.get('category')
            )
            return jsonify(expense.to_dict()), 201
        
        @app.route('/api/expenses', methods=['GET'])
        def get_expenses():
            """Get all expenses."""
            return jsonify([exp.to_dict() for exp in manager.expenses])
        
        @app.route('/api/analysis', methods=['GET'])
        def get_analysis():
            """Get spending analysis."""
            analyzer = manager.get_analyzer()
            advisor = manager.get_advisor()
            
            return jsonify({
                'statistics': analyzer.calculate_statistics(),
                'category_totals': analyzer.get_category_totals(),
                'top_category': analyzer.get_top_category()[0],
                'anomalies': [exp.to_dict() for exp in analyzer.detect_anomalies()],
                'advice': advisor.generate_advice()
            })
        
        return app
    except ImportError:
        print("Flask not installed. Install with: pip install flask flask-cors")
        return None


# =====================================================
# DEMO & MAIN EXECUTION
# =====================================================

def main():
    """Demo the Finance Coach system."""
    print("="*60)
    print("AI Personal Finance & Expense Coach - Python Backend")
    print("="*60)
    
    # Create expense manager
    manager = ExpenseManager()
    
    # Add expenses using natural language
    text_input = """
    Coffee at Starbucks $5.50
    Uber ride to work $12.00
    Lunch at Italian restaurant $28.75
    Groceries at Whole Foods $85.00
    Netflix subscription $15.99
    Gym membership $45.00
    Dinner with friends $67.50
    Gas for car $55.00
    Movie tickets $32.00
    Amazon shopping $125.50
    """
    
    print("\n📝 Adding expenses from natural language input...")
    expenses = manager.add_expenses_from_text(text_input)
    print(f"✅ Added {len(expenses)} expenses\n")
    
    # Get analysis
    analyzer = manager.get_analyzer()
    
    print("📊 SPENDING ANALYSIS")
    print("-" * 60)
    print(f"Total Spending: ${analyzer.get_total_spending():.2f}")
    print(f"Average Transaction: ${analyzer.get_average_transaction():.2f}")
    print(f"Number of Transactions: {len(manager.expenses)}")
    
    print("\n💳 CATEGORY BREAKDOWN")
    print("-" * 60)
    for category, amount in sorted(
        analyzer.get_category_totals().items(), 
        key=lambda x: x[1], 
        reverse=True
    ):
        percentage = (amount / analyzer.get_total_spending()) * 100
        print(f"{category.capitalize():15} ${amount:7.2f} ({percentage:5.1f}%)")
    
    # Detect anomalies
    print("\n⚠️  UNUSUAL SPENDING DETECTED")
    print("-" * 60)
    anomalies = analyzer.detect_anomalies()
    if anomalies:
        for exp in anomalies:
            avg = analyzer.get_average_transaction()
            percent_above = ((exp.amount / avg) - 1) * 100
            print(f"• {exp.description}: ${exp.amount:.2f} "
                  f"({percent_above:.0f}% above average)")
    else:
        print("No unusual spending patterns detected!")
    
    # Get advice
    print("\n💡 PERSONALIZED FINANCIAL ADVICE")
    print("-" * 60)
    advisor = manager.get_advisor()
    for tip in advisor.generate_advice():
        print(f"• {tip}\n")
    
    # Statistics
    print("📈 DETAILED STATISTICS")
    print("-" * 60)
    stats = analyzer.calculate_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').title():15} ${value:.2f}")
        else:
            print(f"{key.replace('_', ' ').title():15} {value}")
    
    # Export data
    print("\n💾 Exporting data to expenses.json...")
    manager.export_to_json()
    print("✅ Export complete!\n")


if __name__ == "__main__":
    main()
    
    # Uncomment to run Flask API
    # app = create_flask_app()
    # if app:
    #     print("\n🚀 Starting Flask API on http://localhost:5000")
    #     app.run(debug=True, port=5000)