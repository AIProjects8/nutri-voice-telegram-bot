## Data validation rules

### **Optional** felds
When validation fails, *NULL* is returned, no exception raised. For strict validation and exception raised in case of incorrect/missing value remove **Optional** definition.

*For details check models.py*

### Meal:
    ingredients: List[str], "List of food ingredients"
    userId: str, "Internal UserID" -> provided by PostreSQL as an external value.
    timestamp: datetime, "When the meal was recorded"
    Summary: str, "Description of the meal"

### Users:
    userId: str, "Internal UserID"
    yearOfBirth: **Optional**, [int], "Year of birth (must be a four-digit year, not in the future), greater than 1900"
    gender: **Optional**, [str], One of values: male|female|other, "User gender"
    weight: **Optional**, [float], "User weight in kg"
    allergies: List[str], "Known allergies"
    health_issues: List[str], "Known health issues"

### Symptoms:
    summary: str, "Description of symptoms experienced"
    timestamp: datetime, "When symptoms were recorded"
    userId: str, "Internal UserID"

## MongoDB access and operations

> Configuration based on .env file in the main directory

### Initialization, connection to the DB

After calling 

``` import dbmanager ```

the db_manager instance is created and then initialization logic (including connection and collection/index checks) is executed immediately


### Writing data into DB
** RECOMMENDED METHOD WITH DATA VALIDATION **

1. Init DB connection

```import data_tools as dt```

- Connection to the DB is established.
- Check if proper collections do exist.
- Check if proper indexes do exist.

2. Methods
```
insert_meal(document: Dict[str, Any]) -> str: Validate and insert a single meal document.
insert_meals(documents: List[Dict[str, Any]]) -> List[str]: Validate and insert multiple meals documents.
insert_user(document: Dict[str, Any]) -> str: Validate and insert a single user document.
insert_users(documents: List[Dict[str, Any]]) -> List[str]: Validate and insert multiple user documents.
insert_symptom(document: Dict[str, Any]) -> str: Validate and insert a single symptom document.
insert_symptoms(documents: List[Dict[str, Any]]) -> List[str]: Validate and insert multiple symptom documents.

has_user_details(user_id: str) -> bool: Check if user already has details.
get_user_details_json(user_id: str) -> Optional[dict]: Fetch user details as a JSON.
get_user_details(user_id: str) -> Optional[UsersCollection]: Fetch user details as an object.
```

### Usage Example:

```
import data_tools as dt

   meal_doc = {
        "ingredients": [
            "nori (seaweed)",
            "sushi rice",
            "salmon",
            "fish filling (unidentified)",
            "wasabi",
            "pickled ginger (gari)"
        ],
        "userId": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": datetime.fromisoformat("2025-04-06T14:32:00"),
        "Summary": "Six maki sushi rolls with two fillings, wasabi, and gari."
    }

    meal_id = dt.insert_meal(meal_doc)
    print(f"Inserted meal with ID: {meal_id}")
```

* Full example is in example.py *

### Using the DB manager directly

** Warning! UNRECOMMENDED approach **

Anywhere in your code, you can use:

``` 
from dbmanager import db_manager 
db_manager.insert_one("users", {"email": "test@example.com", "username": "tester"})
```

This is direct write operation into the DB
Existing, standard collections: 
- meals
- users
- symptopms

### Predefinied DB Objects

* See __init__.py *

```
required_collections = ["users", "meals", "symptoms"]
required_indexes = {
    "meals": [ [("userId", 1)], [("timestamp", 1)] ],                
    "users": [ [("userId", 1)] ],
    "symptoms": [ [("userId", 1)], [("timestamp", 1)] ]
```
