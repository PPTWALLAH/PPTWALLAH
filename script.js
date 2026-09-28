let currentStep = 1;

let selectedPlanName = "Normal";
let selectedPlanPrice = 99;


// ============================
// START CREATION
// ============================

function startCreating() {

    document.getElementById("creator").scrollIntoView({
        behavior: "smooth"
    });

}


// ============================
// STEP NAVIGATION
// ============================

function showStep(step) {

    document.querySelectorAll(".step").forEach(function(element) {

        element.classList.remove("active-step");

    });


    const selectedStep =
        document.getElementById("step" + step);


    if (selectedStep) {

        selectedStep.classList.add("active-step");

    }


    updateProgress(step);

    currentStep = step;

}


function updateProgress(step) {

    const progressBar =
        document.getElementById("progressBar");


    const percentage =
        ((step - 1) / 3) * 100;


    progressBar.style.width =
        percentage + "%";


    for (let i = 1; i <= 4; i++) {

        const circle =
            document.getElementById(
                "stepCircle" + i
            );


        if (i <= step) {

            circle.classList.add("active");

        } else {

            circle.classList.remove("active");

        }

    }

}


function nextStep(step) {

    if (!validateStep(step)) {

        return;

    }


    if (step === 3) {

        updateReview();

    }


    showStep(step + 1);


    document.getElementById("creator").scrollIntoView({
        behavior: "smooth"
    });

}


function previousStep(step) {

    showStep(step - 1);

}


// ============================
// VALIDATION
// ============================

function validateStep(step) {


    if (step === 1) {

        const name =
            document.getElementById("name").value.trim();

        const email =
            document.getElementById("email").value.trim();

        const mobile =
            document.getElementById("mobile").value.trim();


        if (name === "") {

            alert("Please enter your name.");

            return false;

        }


        if (!email || !email.includes("@")) {

            alert("Please enter a valid email address.");

            return false;

        }


        if (!/^[0-9]{10}$/.test(mobile)) {

            alert("Please enter a valid 10 digit mobile number.");

            return false;

        }

    }



    if (step === 2) {

        const subject =
            document.getElementById("subject").value;

        const topic =
            document.getElementById("topic").value.trim();

        const style =
            document.getElementById("style").value;


        if (!subject) {

            alert("Please select a subject.");

            return false;

        }


        if (!topic) {

            alert("Please enter your PPT topic.");

            return false;

        }


        if (!style) {

            alert("Please select a presentation style.");

            return false;

        }

    }



    if (step === 3) {

        if (!selectedPlanName) {

            alert("Please select a plan.");

            return false;

        }

    }


    return true;

}


// ============================
// PLAN SELECTION
// ============================

function selectPlan(card) {

    document.querySelectorAll(".plan-card").forEach(function(item) {

        item.classList.remove("selected");

    });


    card.classList.add("selected");


    selectedPlanName =
        card.getAttribute("data-plan");


    selectedPlanPrice =
        Number(card.getAttribute("data-price"));


    updatePrice();

}


// ============================
// PRICE CALCULATION
// ============================

function updatePrice() {

    const slides =
        Number(document.getElementById("slides").value);


    let extraSlides = 0;


    if (slides > 10) {

        extraSlides =
            (slides - 10) * 10;

    }


    const total =
        selectedPlanPrice + extraSlides;


    const advance =
        Math.ceil(total * 0.30);


    const remaining =
        total - advance;


    document.getElementById("selectedPlan").textContent =
        selectedPlanName;


    document.getElementById("totalPrice").textContent =
        "₹" + total;


    document.getElementById("advancePrice").textContent =
        "₹" + advance;


    document.getElementById("remainingPrice").textContent =
        "₹" + remaining;

}


// ============================
// REVIEW
// ============================

function updateReview() {

    const slides =
        document.getElementById("slides").value;


    const totalText =
        document.getElementById("totalPrice").textContent;


    document.getElementById("reviewName").textContent =
        document.getElementById("name").value;


    document.getElementById("reviewEmail").textContent =
        document.getElementById("email").value;


    document.getElementById("reviewMobile").textContent =
        "+91 " +
        document.getElementById("mobile").value;


    document.getElementById("reviewSubject").textContent =
        document.getElementById("subject").value;


    document.getElementById("reviewTopic").textContent =
        document.getElementById("topic").value;


    document.getElementById("reviewSlides").textContent =
        slides + " Slides";


    document.getElementById("reviewLanguage").textContent =
        document.getElementById("language").value;


    document.getElementById("reviewStyle").textContent =
        document.getElementById("style").value;


    document.getElementById("reviewPlan").textContent =
        selectedPlanName;


    document.getElementById("reviewPrice").textContent =
        totalText;

}


// ============================
// SUBMIT REQUEST
// ============================
// FLASK BACKEND CONNECTION
// ============================

async function submitRequest() {

    const agree =
        document.getElementById("agree").checked;


    if (!agree) {

        alert(
            "Please confirm that your information is correct and accept the payment terms."
        );

        return;

    }


    // Collect all form data

    const requestData = {

        name:
            document.getElementById("name").value.trim(),

        email:
            document.getElementById("email").value.trim(),

        mobile:
            document.getElementById("mobile").value.trim(),

        subject:
            document.getElementById("subject").value,

        topic:
            document.getElementById("topic").value.trim(),

        slides:
            document.getElementById("slides").value,

        language:
            document.getElementById("language").value,

        style:
            document.getElementById("style").value,

        graphics:
            document.getElementById("graphics").value,

        requirements:
            document.getElementById("requirements").value.trim(),

        plan:
            selectedPlanName,

        totalPrice:
            document.getElementById("totalPrice").textContent,

        advance:
            document.getElementById("advancePrice").textContent,

        remaining:
            document.getElementById("remainingPrice").textContent

    };


    console.log(
        "Sending request to Flask:",
        requestData
    );


    try {

        // Send data to Flask

        const response = await fetch(
            "/submit-request",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(requestData)

            }
        );


        // Convert Flask response to JSON

        const result =
            await response.json();


        console.log(
            "Flask response:",
            result
        );


        // ============================
        // SUCCESS
        // ============================

        if (result.success) {

            alert(
                "Request submitted successfully!\n\nRequest ID: "
                + result.request_id
            );


            // Hide all steps

            document.querySelectorAll(".step").forEach(
                function(element) {

                    element.style.display =
                        "none";

                }
            );


            // Hide progress bar

            const progress =
                document.querySelector(
                    ".progress-container"
                );


            if (progress) {

                progress.style.display =
                    "none";

            }


            // Show success card

            document.getElementById(
                "successCard"
            ).style.display =
                "block";


            document.getElementById(
                "successCard"
            ).scrollIntoView({

                behavior: "smooth"

            });


        } else {

            alert(
                "Request submit nahi hui.\n\n" +
                result.message
            );

        }


    } catch (error) {

        console.error(
            "Backend Error:",
            error
        );


        alert(
            "Flask backend se connection nahi ho raha.\n\n" +
            "Please check that app.py is running."
        );

    }

}


// ============================
// INITIAL PRICE
// ============================

updatePrice();