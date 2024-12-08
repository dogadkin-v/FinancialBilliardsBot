import datetime

CASH_RATE = 20
COMMISSION = 10


class Users:
    """Базовый класс для всех пользователей"""

    def __init__(self, users_data):
        if users_data is not None and len(users_data) > 0:
            self.users = users_data
        else:
            self.users = []
        #Можно ввести тестовые данные для инициализации
        # self.users = [
        #     {
        #         'id': 1,
        #         'name': 'Кустов Артем',
        #         'debt': {
        #             datetime.date(2024, 10, 27): 20,
        #             datetime.date(2024, 10, 28): 20
        #         },
        #         'debt_bonus': 20,
        #         'sum_debt': 40
        #     }
        # ]

    def add_user(self, user):
        user['debt'] = {}
        user['debt_bonus'] = 0
        user['sum_debt'] = 0
        self.users.append(user)

    def get_users(self):
        return self.users

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user

    def calc_and_set_bonus(self, date_key):
        for user in self.users:
            if (user['debt'].get(date_key) is not None):
                break
            user['debt'].setdefault(date_key, 0)
            data = self.calculate_debt_and_bonus(user['debt'])
            user['debt_bonus'] += data['bonus']
            user['sum_debt'] = data['sum_debt']

    def calculate_debt_and_bonus(self, data):
        total_sum = 0
        previous_sum = 0
        bonus = 0
        sorted_dates = sorted(data.keys())

        for i, date in enumerate(sorted_dates):
            value = data[date]

            # Прибавляем текущее значение к общей сумме
            total_sum += value

            # Если это не первая дата, то добавляем бонус
            if i > 0:
                bonus += previous_sum * 0.1
                previous_sum = total_sum - value

        return {
            'sum_debt': total_sum,
            'bonus': bonus
        }

    def win_loser_debt(self, user, date_key):
        debt = user['debt']
        sorted_dates = sorted(debt.keys())
        for i, date in enumerate(sorted_dates):
            if i == 0:
                value = debt[date]
                if value:
                    debt[date] -= CASH_RATE
                    user['sum_debt'] -= CASH_RATE
                if debt[date] <= 0:
                    del debt[date]
                break


        sorted_dates = sorted(debt.keys())
        sum_debt = 0
        for i, date in enumerate(sorted_dates):
            value = debt[date]
            sum_debt += value
        if sum_debt == 0 and not(len(sorted_dates) == 1 and sorted_dates[0] == date_key):
            debt.clear()


    def set_win(self, id):
        date_key = datetime.datetime.now().date()

        self.calc_and_set_bonus(date_key)

        winner = self.get_user_by_id(id)
        loser = list(filter(lambda user: user['id'] != id, self.users))[0]
        if winner['sum_debt'] > 0 and winner['sum_debt'] >= CASH_RATE:
            self.win_loser_debt(winner, date_key)
        elif 0 < winner['sum_debt'] <= CASH_RATE:
            loser['debt'][date_key] += CASH_RATE - winner['sum_debt']
            loser['sum_debt'] += CASH_RATE - winner['sum_debt']
            self.win_loser_debt(winner, date_key)
        elif winner['sum_debt'] <=0 and winner['debt_bonus'] >CASH_RATE:
            winner['debt_bonus'] -= CASH_RATE
        else:
            loser['debt'][date_key] += CASH_RATE
            loser['sum_debt'] += CASH_RATE
            if winner['debt_bonus']:
                loser['debt'][date_key] -= winner['debt_bonus']
                loser['sum_debt'] -= winner['debt_bonus']
                winner['debt_bonus'] = 0

    def get_loser(self):
        debt = 0
        loser = None

        for user in self.users:
            if (user_debt := user['sum_debt']) > debt or user['debt_bonus']:
                debt = user_debt
                loser = user
        return loser

    def pay_off_debt(self):
        for user in self.users:
            user['debt_bonus'] = 0
            user['sum_debt'] = 0
            user['debt'].clear()

