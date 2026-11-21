from dataclasses import dataclass
from typing import List, Optional

from drafter import *


# -----------------------------
# Website information
# -----------------------------

set_website_title("Stormwater Solutions")
set_site_information(
    author="Your Name",
    description=(
        "An educational calculator that estimates property stormwater "
        "runoff and compares sustainable drainage solutions."
    ),
    sources=(
        "Drafter documentation. Runoff coefficients and solution costs "
        "in this beginner version are illustrative example values, not "
        "verified local engineering data."
    ),
    planning="See the planning document and website mock-up in the repository.",
    links=[
        "https://drafter-edu.github.io/drafter/",
        "https://www.epa.gov/soakuptherain"
    ]
)


# -----------------------------
# Data classes
# -----------------------------

@dataclass
class Solution:
    """Store the information for one stormwater management solution."""
    name: str
    cost: float
    reduction: float
    description: str
    environmental_benefit: str


@dataclass
class State:
    """Store information that is shared between website routes."""
    property_area: float
    rainfall: float
    surface_type: str
    budget: float
    runoff_volume: float
    solutions: List[Solution]
    saved_solutions: List[Solution]
    message: str


# -----------------------------
# Example data and constants
# -----------------------------

GALLONS_PER_CUBIC_FOOT = 7.48052

# These coefficients are simplified examples for a class project.
# They should not be treated as site-specific engineering values.
RUNOFF_COEFFICIENTS = {
    "Concrete": 0.90,
    "Asphalt": 0.85,
    "Roof": 0.95,
    "Grass": 0.20,
    "Soil": 0.30
}


def make_solutions() -> List[Solution]:
    """Create the small example database of drainage solutions."""
    return [
        Solution(
            "Rain Garden",
            800.0,
            40.0,
            "A planted area that collects and absorbs rainwater.",
            "Can support pollinators and help filter some pollutants."
        ),
        Solution(
            "Permeable Pavement",
            1200.0,
            55.0,
            "Pavement that lets water pass through into a stone base.",
            "Can reduce surface runoff and support groundwater recharge."
        ),
        Solution(
            "Green Roof",
            2000.0,
            30.0,
            "A roof covered with vegetation and a growing medium.",
            "Can provide habitat, reduce roof temperatures, and retain rain."
        )
    ]


def calculate_runoff(area: float, rainfall: float,
                     surface_type: str) -> float:
    """Estimate runoff volume in gallons for one surface type."""
    coefficient = RUNOFF_COEFFICIENTS[surface_type]
    rainfall_feet = rainfall / 12
    runoff_cubic_feet = area * rainfall_feet * coefficient
    return runoff_cubic_feet * GALLONS_PER_CUBIC_FOOT


def get_affordable_solutions(solutions: List[Solution],
                             budget: float) -> List[Solution]:
    """Return only solutions with an estimated cost within the budget."""
    affordable = []
    for solution in solutions:
        if solution.cost <= budget:
            affordable.append(solution)
    return affordable


def find_solution(solutions: List[Solution],
                  solution_name: str) -> Optional[Solution]:
    """Find a solution by name; return None when no match is found."""
    for solution in solutions:
        if solution.name == solution_name:
            return solution
    return None


# -----------------------------
# Routes
# -----------------------------

@route
def index(state: State) -> Page:
    """Show the homepage and links to the main website sections."""
    return Page(state, [
        Header("Stormwater Solutions"),
        "Calculate estimated runoff from your property.",
        "Then compare practical ways to reduce that runoff.",
        Header("Get Started", 2),
        Button("Open the Runoff Calculator", "calculator"),
        Button("Compare Drainage Solutions", "compare_solutions"),
        Button("View Saved Solutions", "saved_plans"),
        Button("Learn About Stormwater", "learn"),
        Button("About This Website", "about")
    ])


@route
def calculator(state: State) -> Page:
    """Show the form for entering property and budget information."""
    return Page(state, [
        Header("Stormwater Runoff Calculator"),
        "For this first version, choose one main surface type.",
        "Property area (square feet):",
        TextBox("area", state.property_area, kind="number"),
        "Rainfall (inches):",
        TextBox("rainfall", state.rainfall, kind="number"),
        "Main surface type:",
        SelectBox(
            "surface",
            ["Concrete", "Asphalt", "Roof", "Grass", "Soil"],
            state.surface_type
        ),
        "Maximum budget for a solution ($):",
        TextBox("budget", state.budget, kind="number"),
        Button("Calculate Runoff", "calculate_runoff_route"),
        Button("Back Home", "index")
    ])


@route
def calculate_runoff_route(state: State, area: float,
                            rainfall: float, surface: str,
                            budget: float) -> Page:
    """Validate the inputs, update state, and calculate runoff."""
    if area <= 0:
        state.message = "Property area must be greater than zero."
        return Page(state, [
            Header("Input Error"),
            state.message,
            Button("Return to Calculator", "calculator")
        ])

    if rainfall < 0:
        state.message = "Rainfall cannot be negative."
        return Page(state, [
            Header("Input Error"),
            state.message,
            Button("Return to Calculator", "calculator")
        ])

    if budget < 0:
        state.message = "Budget cannot be negative."
        return Page(state, [
            Header("Input Error"),
            state.message,
            Button("Return to Calculator", "calculator")
        ])

    if surface not in RUNOFF_COEFFICIENTS:
        state.message = "Please select a valid surface type."
        return Page(state, [
            Header("Input Error"),
            state.message,
            Button("Return to Calculator", "calculator")
        ])

    state.property_area = area
    state.rainfall = rainfall
    state.surface_type = surface
    state.budget = budget
    state.runoff_volume = calculate_runoff(area, rainfall, surface)
    state.message = "Your runoff estimate is ready."

    return results(state)


@route
def results(state: State) -> Page:
    """Display the runoff estimate and the entered property details."""
    return Page(state, [
        Header("Your Runoff Results"),
        "Property area: " + str(state.property_area) + " square feet",
        "Rainfall: " + str(state.rainfall) + " inches",
        "Surface type: " + state.surface_type,
        Header(
            str(round(state.runoff_volume, 1)) + " gallons estimated runoff",
            2
        ),
        "This is a simplified estimate, not an engineered drainage design.",
        Button("Compare Solutions Within My Budget", "compare_solutions"),
        Button("Change My Inputs", "calculator"),
        Button("Back Home", "index")
    ])


@route
def compare_solutions(state: State) -> Page:
    """Loop through the solution database and show affordable options."""
    affordable = get_affordable_solutions(
        state.solutions, state.budget
    )

    content = [
        Header("Compare Drainage Solutions"),
        "Your budget: $" + str(round(state.budget, 2)),
        "Costs and reduction percentages are example values."
    ]

    if len(affordable) == 0:
        content.append("No example solutions fit this budget.")
        content.append("Return to the calculator to change your budget.")
    else:
        for solution in affordable:
            content.append(Header(solution.name, 2))
            content.append(
                "Estimated cost: $" + str(round(solution.cost, 2))
            )
            content.append(
                "Estimated runoff reduction: "
                + str(solution.reduction) + "%"
            )
            content.append(solution.description)
            content.append(
                "Environmental benefit: "
                + solution.environmental_benefit
            )
            content.append(Button(
                "Save " + solution.name,
                "save_solution",
                [("solution_name", solution.name)]
            ))

    content.append(Button("View Saved Solutions", "saved_plans"))
    content.append(Button("Back to Results", "results"))
    content.append(Button("Back Home", "index"))
    return Page(state, content)


@route
def save_solution(state: State, solution_name: str) -> Page:
    """Add a solution to the saved list unless it is already saved."""
    selected = find_solution(state.solutions, solution_name)
    already_saved = find_solution(
        state.saved_solutions, solution_name
    )

    if selected is None:
        state.message = "That solution could not be found."
    elif already_saved is not None:
        state.message = "That solution is already in your saved list."
    else:
        state.saved_solutions.append(selected)
        state.message = solution_name + " was saved."

    return saved_plans(state)


@route
def saved_plans(state: State) -> Page:
    """Display saved solutions by looping through the saved list."""
    content = [
        Header("Your Saved Solutions"),
        state.message
    ]

    if len(state.saved_solutions) == 0:
        content.append("You have not saved any solutions yet.")
    else:
        for solution in state.saved_solutions:
            content.append(Header(solution.name, 2))
            content.append(
                "Estimated cost: $" + str(round(solution.cost, 2))
            )
            content.append(
                "Estimated runoff reduction: "
                + str(solution.reduction) + "%"
            )
            content.append(Button(
                "Remove " + solution.name,
                "remove_solution",
                [("solution_name", solution.name)]
            ))

    content.append(Button("Compare Solutions", "compare_solutions"))
    content.append(Button("Back Home", "index"))
    return Page(state, content)


@route
def remove_solution(state: State, solution_name: str) -> Page:
    """Remove the named solution from the saved-solutions list."""
    remaining_solutions = []

    for solution in state.saved_solutions:
        if solution.name != solution_name:
            remaining_solutions.append(solution)

    state.saved_solutions = remaining_solutions
    state.message = solution_name + " was removed."
    return saved_plans(state)


@route
def about(state: State) -> Page:
    """Explain the purpose and limitations of the website."""
    return Page(state, [
        Header("About This Website"),
        "Stormwater Solutions is an educational project about runoff.",
        "It estimates runoff and compares several sustainable drainage "
        "options using a small collection of example data.",
        "Actual costs and performance depend on soil, design, location, "
        "maintenance, and other site conditions.",
        Button("Back Home", "index")
    ])


@route
def learn(state: State) -> Page:
    """Explain why runoff happens and introduce three solutions."""
    return Page(state, [
        Header("Learn About Stormwater"),
        Header("Why does runoff happen?", 2),
        "Hard surfaces such as roofs and pavement prevent rainwater "
        "from soaking into the ground.",
        Header("Rain gardens", 2),
        "Rain gardens collect runoff and allow it to soak into soil.",
        Header("Permeable pavement", 2),
        "Permeable pavement lets water pass through into a stone base.",
        Header("Green roofs", 2),
        "Green roofs use plants and growing media to hold some rainfall.",
        Button("Compare Solutions", "compare_solutions"),
        Button("Back Home", "index")
    ])


# -----------------------------
# Basic tests for helper functions
# -----------------------------

def test_calculate_runoff() -> None:
    """Check basic expected behavior of the runoff calculation."""
    assert calculate_runoff(1000, 0, "Concrete") == 0
    assert calculate_runoff(1000, 1, "Concrete") > 0


def test_get_affordable_solutions() -> None:
    """Check that the budget filter excludes solutions over budget."""
    example_solutions = make_solutions()
    affordable = get_affordable_solutions(example_solutions, 1000)

    for solution in affordable:
        assert solution.cost <= 1000


# Run helper tests before starting the website.
test_calculate_runoff()
test_get_affordable_solutions()


# Start the Drafter website.
start_server(State(
    property_area=1000.0,
    rainfall=1.0,
    surface_type="Concrete",
    budget=1500.0,
    runoff_volume=0.0,
    solutions=make_solutions(),
    saved_solutions=[],
    message="Welcome! Enter your property information to begin."
))

