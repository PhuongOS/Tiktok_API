"""
Rule evaluation engine
"""
from typing import Dict, List, Any
from app.models.rule import Rule, RuleCondition, ComparisonOperator
import logging
import re

logger = logging.getLogger(__name__)


class RuleEvaluator:
    """Evaluate rules against events"""
    
    @staticmethod
    def evaluate_rule(rule: Rule, event: Dict[str, Any]) -> bool:
        """
        Evaluate if rule matches event
        
        Returns True if rule should trigger
        """
        # Check event type
        if rule.event_type != event.get("event_type"):
            return False
        
        # Check livestream filter
        if rule.livestream_id and rule.livestream_id != event.get("livestream_id"):
            return False
        
        # Evaluate conditions
        if not rule.conditions:
            return True  # No conditions = always match
        
        condition_results = [
            RuleEvaluator._evaluate_condition(cond, event)
            for cond in sorted(rule.conditions, key=lambda c: c.order)
        ]
        
        # Apply logic operator
        if rule.logic_operator == "AND":
            return all(condition_results)
        elif rule.logic_operator == "OR":
            return any(condition_results)
        else:
            logger.error(f"Unknown logic operator: {rule.logic_operator}")
            return False
    
    @staticmethod
    def _evaluate_condition(condition: RuleCondition, event: Dict[str, Any]) -> bool:
        """Evaluate single condition"""
        # Get field value from event
        field_value = event.get(condition.field)
        
        if field_value is None:
            return False
        
        # Convert condition value to appropriate type
        expected_value = RuleEvaluator._convert_value(condition.value, field_value)
        
        # Apply operator
        operator = condition.operator
        
        try:
            if operator == ComparisonOperator.EQUALS:
                return field_value == expected_value
            
            elif operator == ComparisonOperator.NOT_EQUALS:
                return field_value != expected_value
            
            elif operator == ComparisonOperator.GREATER_THAN:
                return float(field_value) > float(expected_value)
            
            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return float(field_value) >= float(expected_value)
            
            elif operator == ComparisonOperator.LESS_THAN:
                return float(field_value) < float(expected_value)
            
            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                return float(field_value) <= float(expected_value)
            
            elif operator == ComparisonOperator.CONTAINS:
                return str(expected_value).lower() in str(field_value).lower()
            
            elif operator == ComparisonOperator.NOT_CONTAINS:
                return str(expected_value).lower() not in str(field_value).lower()
            
            elif operator == ComparisonOperator.IN:
                # expected_value should be comma-separated list
                values = [v.strip() for v in str(expected_value).split(",")]
                return str(field_value) in values
            
            elif operator == ComparisonOperator.NOT_IN:
                values = [v.strip() for v in str(expected_value).split(",")]
                return str(field_value) not in values
            
            else:
                logger.error(f"Unknown operator: {operator}")
                return False
        
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    @staticmethod
    def _convert_value(value_str: str, reference_value: Any) -> Any:
        """Convert string value to appropriate type"""
        # Try to match type of reference value
        if isinstance(reference_value, bool):
            return value_str.lower() in ["true", "1", "yes"]
        elif isinstance(reference_value, int):
            try:
                return int(value_str)
            except ValueError:
                return value_str
        elif isinstance(reference_value, float):
            try:
                return float(value_str)
            except ValueError:
                return value_str
        else:
            return value_str
