import sqlite3

def check_authorized_manager(cur, manager_name, account_id):
    cur.execute('''
    SELECT 1 FROM account WHERE id = ? AND authorized_manager = ?
    ''', (account_id, manager_name))
    return cur.fetchone() is not None

def transfer_hours(manager_name, from_account_id, to_account_id, hours):
    con = sqlite3.connect('database_name.db')
    cur = con.cursor()

    # Check if the manager is authorized to manage both accounts
    if not (check_authorized_manager(cur, manager_name, from_account_id) and
            check_authorized_manager(cur, manager_name, to_account_id)):
        print("Manager is not authorized to manage both accounts.")
        con.close()
        return

    # Check if from_account has enough hours to transfer
    cur.execute('''
    SELECT hours_allocated FROM account WHERE id = ?
    ''', (from_account_id,))
    from_account_hours = cur.fetchone()
    if not from_account_hours or from_account_hours[0] < hours:
        print("Not enough hours to transfer.")
        con.close()
        return

    # Perform the hours transfer
    cur.execute('''
    UPDATE account SET hours_allocated = hours_allocated - ? WHERE id = ?
    ''', (hours, from_account_id))
    cur.execute('''
    UPDATE account SET hours_allocated = hours_allocated + ? WHERE id = ?
    ''', (hours, to_account_id))

    con.commit()
    con.close()
    print(f"Transferred {hours} hours from account {from_account_id} to account {to_account_id}.")

# Example usage
if __name__ == "__main__":
    manager_name = input("Enter authorized manager name: ")
    from_account_id = int(input("Enter source account ID: "))
    to_account_id = int(input("Enter destination account ID: "))
    hours = int(input("Enter number of hours to transfer: "))

    transfer_hours(manager_name, from_account_id, to_account_id, hours)
