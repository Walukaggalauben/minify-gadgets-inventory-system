const customerSearch = document.getElementById("customerSearch");

if (customerSearch) {
  const customerResults = document.getElementById("customerResults");

  const customerId = document.getElementById("customer_id");

  const selectedCard = document.getElementById("selectedCustomerCard");

  const selectedName = document.getElementById("selectedCustomerName");

  const selectedPhone = document.getElementById("selectedCustomerPhone");

  customerSearch.addEventListener("keyup", async function () {
    const query = this.value.trim();

    if (query.length < 2) {
      customerResults.style.display = "none";

      customerResults.innerHTML = "";

      return;
    }

    const response = await fetch(
      `/customers/api/search?q=${encodeURIComponent(query)}`,
    );

    const customers = await response.json();

    customerResults.innerHTML = "";

    if (!customers.length) {
      customerResults.style.display = "none";

      return;
    }

    customerResults.style.display = "block";

    customers.forEach((customer) => {
      const item = document.createElement("button");

      item.type = "button";

      item.className = "list-group-item list-group-item-action";

      item.innerHTML = `
                <strong>${customer.name}</strong><br>
                <small>${customer.phone}</small>
            `;

      item.onclick = () => {
        customerSearch.value = `${customer.name} (${customer.phone})`;

        customerId.value = customer.id;

        selectedName.textContent = customer.name;

        selectedPhone.textContent = customer.phone;

        selectedCard.style.display = "block";

        customerResults.style.display = "none";

        customerResults.innerHTML = "";

        // Auto-fill Trade-In form if the fields exist

        const setValue = (name, value) => {
          const field = document.querySelector(`[name="${name}"]`);
          if (field) {
            field.value = value || "";
          }
        };

        setValue("customer_name", customer.name);
        setValue("phone_number", customer.phone);
        setValue("alternative_phone", customer.alternative_phone);
        setValue("business_name", customer.business_name);
        setValue("email", customer.email);
        setValue("national_id", customer.national_id);
        setValue("address", customer.address);
      };

      customerResults.appendChild(item);
    });
  });
}

// ==============================================
// REGISTER NEW CUSTOMER
// ==============================================

const registerCustomerBtn =
    document.getElementById("registerCustomerBtn");

registerCustomerBtn?.addEventListener(
    "click",
    function () {

        window.open(
            "/customers/create",
            "_blank"
        );

    }
);
