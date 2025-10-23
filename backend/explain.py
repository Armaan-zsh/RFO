"""
AI explainer for rocket fuel optimization results.
"""
from typing import Dict, Any, List


def explain_run(params: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI explanations for experiment results.
    
    Args:
        params: Experiment parameters
        results: Experiment results
        
    Returns:
        Dictionary with explanations and suggestions
    """
    # Extract key values
    thrust = results.get('simulation', {}).get('thrust', 0)
    temp = params.get('temp', 3000)
    pressure = params.get('pressure', 5)
    of_ratio = params.get('O_F_ratio', 3.5)
    
    # Generate summary
    summary = _generate_summary(thrust, temp, pressure, of_ratio)
    
    # Generate physical explanations
    physical_reasons = _generate_physical_reasons(params, results)
    
    # Generate experiment suggestions
    suggestions = _generate_suggestions(params, results)
    
    # Generate beginner explanation
    beginner_explanation = _generate_beginner_explanation(params, results)
    
    return {
        'summary': summary,
        'physical_reasons': physical_reasons,
        'suggestions': suggestions,
        'beginner_explanation': beginner_explanation
    }


def _generate_summary(thrust: float, temp: float, pressure: float, of_ratio: float) -> str:
    """Generate one-sentence summary of the run outcome."""
    performance = "high" if thrust > 300 else "moderate" if thrust > 200 else "low"
    return f"The rocket configuration achieved {performance} performance with {thrust:.1f} kN thrust at {temp:.0f}K combustion temperature."


def _generate_physical_reasons(params: Dict[str, Any], results: Dict[str, Any]) -> List[str]:
    """Generate physical explanations for the results."""
    reasons = []
    
    thrust = results.get('simulation', {}).get('thrust', 0)
    temp = params.get('temp', 3000)
    pressure = params.get('pressure', 5)
    of_ratio = params.get('O_F_ratio', 3.5)
    
    # Temperature analysis
    if temp > 3500:
        reasons.append("High combustion temperature increases molecular kinetic energy, boosting exhaust velocity and thrust.")
    elif temp < 2800:
        reasons.append("Lower combustion temperature reduces exhaust velocity, limiting thrust potential.")
    else:
        reasons.append("Moderate combustion temperature provides balanced performance between thrust and thermal stress.")
    
    # Pressure analysis
    if pressure > 7:
        reasons.append("High chamber pressure increases mass flow rate through the nozzle, directly boosting thrust output.")
    elif pressure < 3:
        reasons.append("Low chamber pressure limits mass flow rate, reducing overall thrust generation.")
    else:
        reasons.append("Moderate chamber pressure provides stable combustion with reasonable thrust levels.")
    
    # O/F ratio analysis
    if of_ratio > 4.5:
        reasons.append("High oxidizer-to-fuel ratio may cause incomplete combustion, reducing efficiency despite excess oxidizer.")
    elif of_ratio < 2.5:
        reasons.append("Low oxidizer-to-fuel ratio creates fuel-rich conditions, potentially reducing combustion temperature.")
    else:
        reasons.append("Balanced oxidizer-to-fuel ratio promotes complete combustion and optimal energy release.")
    
    return reasons[:3]  # Return top 3 reasons


def _generate_suggestions(params: Dict[str, Any], results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate experiment suggestions with expected changes."""
    suggestions = []
    
    current_temp = params.get('temp', 3000)
    current_pressure = params.get('pressure', 5)
    current_of = params.get('O_F_ratio', 3.5)
    
    # Temperature suggestion
    if current_temp < 3500:
        suggestions.append({
            'experiment': f"Increase combustion temperature to {current_temp + 300:.0f}K",
            'expected_thrust': 'positive',
            'expected_temperature': 'positive',
            'risk': 'Higher thermal stress on combustion chamber materials'
        })
    else:
        suggestions.append({
            'experiment': f"Decrease combustion temperature to {current_temp - 200:.0f}K",
            'expected_thrust': 'negative',
            'expected_temperature': 'negative',
            'risk': 'Reduced performance but improved material longevity'
        })
    
    # Pressure suggestion
    if current_pressure < 8:
        suggestions.append({
            'experiment': f"Increase chamber pressure to {current_pressure + 1.5:.1f} MPa",
            'expected_thrust': 'positive',
            'expected_temperature': 'neutral',
            'risk': 'Higher structural loads requiring stronger chamber design'
        })
    else:
        suggestions.append({
            'experiment': f"Decrease chamber pressure to {current_pressure - 1:.1f} MPa",
            'expected_thrust': 'negative',
            'expected_temperature': 'neutral',
            'risk': 'Reduced thrust but lower structural requirements'
        })
    
    # O/F ratio suggestion
    if current_of < 4:
        suggestions.append({
            'experiment': f"Increase O/F ratio to {current_of + 0.5:.1f}",
            'expected_thrust': 'positive',
            'expected_temperature': 'positive',
            'risk': 'Potential oxidizer-rich combustion affecting engine components'
        })
    else:
        suggestions.append({
            'experiment': f"Decrease O/F ratio to {current_of - 0.3:.1f}",
            'expected_thrust': 'negative',
            'expected_temperature': 'negative',
            'risk': 'Fuel-rich combustion may cause carbon buildup'
        })
    
    return suggestions


def _generate_beginner_explanation(params: Dict[str, Any], results: Dict[str, Any]) -> str:
    """Generate intuitive explanation for beginners."""
    thrust = results.get('simulation', {}).get('thrust', 0)
    temp = params.get('temp', 3000)
    
    explanation = f"""
    Think of a rocket engine like a controlled explosion in a metal chamber. The fuel and oxidizer mix and burn at {temp:.0f}K 
    (about {temp/1000:.1f} times hotter than your oven!), creating hot gases that rush out the back at incredible speed. 
    This produces {thrust:.1f} kN of thrust - imagine the force of about {thrust*100:.0f} people pushing together. 
    The key is balancing the mixture: too much fuel wastes oxidizer, too much oxidizer can damage the engine, 
    and the right balance gives maximum push while keeping everything from melting. Higher temperatures and pressures 
    generally mean more thrust, but also more stress on the engine materials.
    """.strip()
    
    return explanation