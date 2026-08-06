from models.customer import Customer


class CustomerService:

    @staticmethod
    def generate_customer_code():

        last = (

            Customer.query

            .order_by(Customer.id.desc())

            .first()

        )

        if last:

            try:

                number = int(

                    last.customer_code.split("-")[-1]

                )

            except Exception:

                number = 0

        else:

            number = 0

        return f"CUST-{number + 1:06d}"