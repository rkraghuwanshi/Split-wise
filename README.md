# Splitwise

This is just a backend imitation of splitwise.

2. Local Setup
   ### Prerequisites
   1. Python 3.9
   2. Pip

```shell
pip install -r requirements.txt
```

3.  Run the command
    `python manage.py makemigrations && python manage.py migrate && python manage.py runserver 8000`
    This will start the server at localhost:8000

### For Usage - Use postman collection provided alongside code

Import the collection to postman and you will be able to see the endpoints and use them
Also set an environment variable in postman

Variable Name = url

Variable Value = http://127.0.0.1:8000/api [local setup]

## The API Supports the below operations though rest endpoints:

1. Create User [/createUser]
2. Create Group [/createGroup]
3. Add member to group [/addUserToGroup]
4. Add personal expense between 2 existing users [/addExpense]
5. Add group expense [/addExpense]
6. Show Group Expenses [/groupDetails]
7. Show Group Members [/showGroupMembers]
8. Show the user balance [/userDetails]
9. Show All user balance [/allUserDetails]
10. Record a personal payment [/recordPayment]
11. Record a group payment [/recordPayment]
12. Delete a user [/deleteUser]
13. Delete a group [/deleteGroup]

## Test Cases

Test cases are available in `expenses/tests.py`

To run the test cases, run the command `python manage.py test`
