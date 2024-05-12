function startListen() {
    $.ajax({
        type: "POST",
        url: "/start_listen",
        success: function(data) {
            console.log(data.message);
            $("#startButton").hide();
            $("#stopButton").show();
            getCount();
        },
        error: function(xhr, status, error) {
            console.error('Erreur lors de la demande:', error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
}

function stopListen() {
    $.ajax({
        type: "POST",
        url: "/stop_listen",
        success: function(data) {
            console.log(data.message);
            $("#stopButton").hide();
            $("#startButton").show();
            getCount();
        },
        error: function(xhr, status, error) {
            console.error('Erreur lors de la demande:', error);
            alert("Une erreur s'est produite. Veuillez réessayer.");
        }
    });
}

function getCount() {
    $.ajax({
        type: "GET",
        url: "/get_count",
        success: function(data) {
            console.log("Nombre de pressions de touches:", data.count);
            if (data.count !== undefined) {
                $("#countDisplay").text("Nombre de pressions de touches : " + data.count);
            }
        },
        error: function(xhr, status, error) {
            console.error('Erreur lors de la demande:', error);
            alert("Une erreur s'est produite lors de la récupération du nombre de pressions de touches.");
        }
    });
}