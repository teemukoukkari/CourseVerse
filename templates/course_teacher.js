var mcq_choice_count = 0;

mcq_add_choice()
mcq_add_choice()
mcq_add_choice()
mcq_add_choice()

function mcq_add_choice() {
    const checkbox = document.createElement("input");
    checkbox.setAttribute("type", "checkbox");
    checkbox.setAttribute("name", "correct_" + mcq_choice_count);

    const text = document.createElement("input");
    text.setAttribute("type", "text");
    text.setAttribute("name", "answer_" + mcq_choice_count)

    const div = document.createElement("div");
    div.setAttribute("id", "mcq_choice" + mcq_choice_count);
    div.appendChild(checkbox);
    div.appendChild(text);

    document.getElementById("mcq_form").append(div);
    mcq_choice_count++;
}

function mcq_remove_choice() {
    if (mcq_choice_count < 2) return;
    const div = document.getElementById("mcq_choice" + (mcq_choice_count-1));
    div.parentNode.removeChild(div);
    mcq_choice_count--;
}

function mcq_submit() {
    document.getElementById("mcq_form").submit();
}

function frq_regex_test() {
    const solution_regex = document.getElementById("frq_solution_regex").value;
    const case_insentive = document.getElementById("frq_case_insensitive").checked;
    const test_string = document.getElementById("frq_test_string").value;

    const expr = new RegExp("^(" + solution_regex + ")$", case_insentive ? "i" : "");
    const result = test_string.match(expr);

    document.getElementById("frq_test_result").innerHTML
        = result ? "correct" : "incorrect";
}