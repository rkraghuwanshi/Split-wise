from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from expenses import serializers, models


class UserProfileApiView(APIView):
    """Test API View"""
    serializer_class = serializers.UserProfileSerializer

    def post(self, request) -> Response:
        """Create a hello message with our name"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            name = serializer.validated_data.get('name')
            return Response({'message': f'User {name} created successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateGroupApiView(APIView):
    """Group Creation View"""
    serializer_class = serializers.GroupSerializer

    def post(self, request) -> Response:
        """ Create a hello message with our name """

        all_users = []
        for user_email in request.data.get('members', []):
            try:
                all_users.append(models.UserProfile.objects.get(email=user_email).id)
            except:
                return Response({'message': f'{request}'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['members'] = all_users
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Group {serializer.data.get("group_name")} Created successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddUserToGroupApiView(APIView):
    """Add member to existing group Creation View"""

    def post(self, request) -> Response:
        """ Create a hello message with our name """
        group_name = request.data.get('group_name')
        user_email = request.data.get('user_email')
        user = models.UserProfile.objects.get(email=user_email)
        group = models.Group.objects.get(group_name=group_name)
        if user not in group.members.all():
            group.members.add(user.id)
            return Response({'message': f'User {user_email} successfully added to group {group.group_name}'})
        return Response({'message': 'User already exists in the group'}, status=status.HTTP_400_BAD_REQUEST)


class ShowGroupMembersApiView(APIView):
    """Show group members"""

    def get(self, request) -> Response:
        """ Create a hello message with our name """
        group_name = request.GET['name']
        try:
            group = models.Group.objects.get(group_name=group_name)
            # all_members = [x.name for x in group.members]
            all_members = [str(x) for x in group.members.all()]
            return Response({'message': f'{all_members}'})
        except models.Group.DoesNotExist:
            return Response(
                {'message': 'Group Does not exist !'
                 },
                status=status.HTTP_404_NOT_FOUND
            )


class ShowUserDetailsApiView(APIView):
    """Show user details"""

    def get(self, request) -> Response:
        user_email = request.GET['email']
        try:
            user = models.UserProfile.objects.get(email=user_email)
            f_debts = models.Debt.objects.filter(from_user=user)
            t_debts = models.Debt.objects.filter(to_user=user)
            debt_data = dict()
            debit = 0
            credit = 0
            for i in f_debts:
                debt_data[i.to_user.name] = debt_data.get(i.to_user.name, 0) - i.amount
                debit -= i.amount
            for i in t_debts:
                debt_data[i.from_user.name] = debt_data.get(i.from_user.name, 0) + i.amount
                credit += i.amount
            return Response(
                {'message':
                    {
                        'user': f'{user}',
                        'debit': debit,
                        'credit': credit,
                        'data': [f'User {user.name} owes {debt_data[x]} to user {x}' if debt_data[
                                                                                           x] > 0 else f'User {user.name} lent {debt_data[x]} to {x}'
                                 for x in debt_data if
                                 x != user.name and debt_data[x] != 0],
                    }
                }
            )
        except models.UserProfile.DoesNotExist:
            return Response(
                {'message': 'User Does not exist !'
                 },
                status=status.HTTP_404_NOT_FOUND
            )
        
class ShowAllUserDetailsApiView(APIView):
    """Show user details"""

    def get(self, request) -> Response:
        try:
            users = models.UserProfile.objects.all()
            resArr=[]
            for user in users:
                f_debts = models.Debt.objects.filter(from_user=user)
                t_debts = models.Debt.objects.filter(to_user=user)
                debt_data = dict()
                debit = 0
                credit = 0
                for i in f_debts:
                    debt_data[i.to_user.name] = debt_data.get(i.to_user.name, 0) - i.amount
                    debit -= i.amount
                for i in t_debts:
                    debt_data[i.from_user.name] = debt_data.get(i.from_user.name, 0) + i.amount
                    credit += i.amount
                resArr.append(
                    {'message':
                        {
                            'user': f'{user}',
                            'debit': debit,
                            'credit': credit,
                            'data': [f'User {user.name} owes {debt_data[x]} to user {x}' if debt_data[
                                                                                            x] > 0 else f'User {user.name} lent {-1*debt_data[x]} to {x}'
                                    for x in debt_data if
                                    x != user.name and debt_data[x] != 0],
                        }
                    }
                )
            return Response(resArr, status=status.HTTP_200_OK)
        except models.UserProfile.DoesNotExist:
            return Response(
                {'message': 'User Does not exist !'
                },
                status=status.HTTP_404_NOT_FOUND
            )
            



class CreateExpenseApiView(APIView):
    serializer_class = serializers.ExpenseSerializer

    def calculate_equal_shares(self, amount, users):
        return round(amount / len(users),2)

    def calculate_exact_shares(self, exact_shares, amount):
        total_share = 0
        amount_share = {}

        # Calculate total percent
        for email, amt in exact_shares.items():
            total_share += amt

        # Check if total percent is 100
        if  total_share!= amount:
            raise ValueError("Total percent does not add up to 100")

        # Calculate amount share based on percent share
        for email, amt in exact_shares.items():
            share = amount-amt
            amount_share[email] = round(share,2)

        return amount_share

    def calculate_percent_share(self,percent_share, total_amount):
        total_percent = 0
        amount_share = {}

        # Calculate total percent
        for email, percent in percent_share.items():
            total_percent += percent

        # Check if total percent is 100
        if total_percent != 100:
            raise ValueError("Total percent does not add up to 100")

        # Calculate amount share based on percent share
        for email, percent in percent_share.items():
            share = (percent / 100) * total_amount
            amount_share[email] = round(share,2)

        return amount_share

    def post(self, request) -> Response:
        description = request.data.get('description')
        all_users = request.data.get('users')
        all_users = models.UserProfile.objects.filter(email__in=all_users)
        paid_by = request.data.get('paid_by')
        paid_by_user = models.UserProfile.objects.filter(email=paid_by).first()
        amount = request.data.get('amount')
        group_name = request.data.get('group_name', None)
        expense_name = request.data.get('name')
        expense_type = request.data.get('expense_type')
        percent_share = request.data.get('user_percent_share',None)
        exact_share = request.data.get('user_exact_share',None)

        group = None
        if group_name is not None:
            group = models.Group.objects.get(group_name=group_name)
        per_member_share = 0
        if(expense_type.lower()=="equal"):
            per_member_share=self.calculate_equal_shares(amount, all_users)
        elif(expense_type.lower()=="exact"):
            if(exact_share==None):
                return Response(
                {'message': 'Please provide exact expense share'
                 },
                status=status.HTTP_400_BAD_REQUEST)
            per_member_share=self.calculate_exact_shares(amount=amount, exact_shares=exact_share)
        elif(expense_type.lower()=="percent"):
            if(percent_share==None):
                return Response(
                {'message': 'Please provide percent expense share'
                 },
                status=status.HTTP_400_BAD_REQUEST)
            per_member_share=self.calculate_percent_share(total_amount=amount, percent_share=percent_share)
        else:
            return Response(
                {'message': 'Please provide valid request json'
                 },
                status=status.HTTP_400_BAD_REQUEST)
        #per_member_share=self.calculate_percent_shares(amount=amount, percent_share=percent_share)
        expense_users = []
        repayments = []
        for user in all_users:
            amt=per_member_share if expense_type.lower()=="equal" else per_member_share[user.email]
            if user != paid_by_user:
                debt = models.Debt.objects.create(**{"from_user": paid_by_user,
                                                     "to_user": user,
                                                     "amount": amt})
                repayments.append(debt)
            expense_user_dict = {"user": user,
                                 "paid_share": 0 if user != paid_by_user else amt,
                                 "owed_share": amt,
                                 "net_balance": -amt if user != paid_by_user else amount - amt
                                 }
            expense_user = models.ExpenseUser.objects.create(**expense_user_dict)
            expense_users.append(expense_user)
        # now create expense
        expense = {
            'expense_group': group,
            'description': description,
            'amount': amount,
            'name': expense_name
        }
        expense = models.Expense.objects.create(**expense)
        expense.repayments.set(repayments)
        expense.users.set(expense_users)
        expense.save()
        return Response({'message': 'Expense Created successfully'})


class ShowGroupDetailsApiView(APIView):
    def get(self, request) -> Response:
        group_name = request.GET['name']
        try:
            group = models.Group.objects.get(group_name=group_name)
            expenses = models.Expense.objects.filter(expense_group=group, payment=False)
            data = list()
            for expense in expenses:
                exp = {
                    "name": expense.name,
                    "Description": expense.description,
                    "repayments": [str(x) for x in expense.repayments.all() if
                                   x.from_user != x.to_user and x.amount != 0]
                }
                data.append(exp)
            return Response(
                {'message': data
                 }
            )
        except models.Group.DoesNotExist:
            return Response(
                {'message': 'Group Does not exist !'
                 },
                status=status.HTTP_404_NOT_FOUND
            )


class DeleteUserApiView(APIView):
    def delete(self, request) -> Response:
        user_email = request.GET['email']
        try:
            user = models.UserProfile.objects.get(email=user_email)
            if user:
                user.delete()
                return Response(
                    {'message': 'User deleted'
                     }
                )
        except models.UserProfile.DoesNotExist:
            return Response({
                "message": "User does not exist"
            })


class DeleteGroupApiView(APIView):
    def delete(self, request) -> Response:
        group_name = request.GET['name']
        try:
            group = models.Group.objects.get(group_name=group_name)
            if group:
                group.delete()
                return Response(
                    {
                        'message': 'Group deleted'
                    }
                )
        except models.Group.DoesNotExist:
            return Response({
                "message": "Group does not exist"
            })


class RecordPaymentApiView(APIView):
    def post(self, request) -> Response:
        from_user_email = request.data.get('from_user')
        to_user_email = request.data.get('to_user')
        amount = request.data.get('amount')
        group_name = request.data.get('group_name')
        expense_name = request.data.get('expense_name')
        from_user = models.UserProfile.objects.get(email=from_user_email)
        to_user = models.UserProfile.objects.get(email=to_user_email)
        try:
            if group_name is None:

                models.Debt.objects.create(**{
                    "from_user": from_user,
                    "to_user": to_user,
                    "amount": amount
                })
                return Response({
                    "message": "Payment recorded successfully"
                })
            else:
                expense = models.Expense.objects.get(name=expense_name)
                if expense.expense_group != models.Group.objects.get(group_name=group_name):
                    return Response({
                        "message": "Expense  not in group, please check !"
                    }, status=status.HTTP_400_BAD_REQUEST)
                flag = False
                for i in expense.repayments.all():
                    if i.from_user == to_user and i.to_user == from_user:
                        flag = True
                        i.amount = i.amount - amount
                        i.save()
                        break
                if not flag:
                    debt = models.Debt.objects.create(**{
                        "from_user": to_user,
                        "to_user": from_user,
                        "amount": amount
                    })
                    expense.repayments.add(debt)
                expense.save()
                flag = False
                for i in expense.repayments.all():
                    if i.amount > 0:
                        flag = True
                        break
                if not flag:
                    expense.payment = True
                    expense.save()
                return Response({
                    "message": "Expense Payment recorded successfully"
                })
        except models.UserProfile.DoesNotExist:
            return Response({
                "message": "User does not exist"
            })
        except models.Expense.DoesNotExist:
            return Response({
                "message": "Expense does not exist"
            })