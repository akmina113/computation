
const dateInputs = document.querySelectorAll('input[type="date"]');
// Format the date to YYYY-MM-DD for HTML input[type=date] compatibility
dateInputs.forEach(input => {
    if (!input.value){
        input.valueAsDate = new Date();
    }
});

//const today = new Date();
//const formattedDate = today.toISOString().split('T')[0];
//dateInput.value = formattedDate;
