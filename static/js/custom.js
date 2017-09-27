$(".dropdown-button").dropdown({
	hover: true,
	belowOrigin: true
});

document.addEventListener("DOMContentLoaded", function() {
	$('.preloader-background').delay(1700).fadeOut('slow');

	$('.preloader-wrapper')
		.delay(1700)
		.fadeOut();
});

$("#addButton").hover(function() {
		$("#addIcon").html("add_circle_outline")
	},
	function() {
		$("#addIcon").html("add_circle")
	}
)

$("#addLBButton").hover(function() {
		$("#addLBIcon").html("add_circle_outline")
	},
	function() {
		$("#addLBIcon").html("add_circle")
	}
)

$(document).ready(function() {
	Materialize.updateTextFields();
	$('#addServer').modal({
		endingTop: '50%',
	});
});

$('input[type=range]').on('input focus mousedown touchstart', function() {
	var label = $("label[for='" + $(this).attr('id') + "']");
	if ($(this).val() < $(this)[0].max / 4) {
		label.css('transform', 'translateY(-50px)');
	} else {
		label.css('transform', '');
	}
});

$('input[type=range]').on('mouseleave touchleave', function() {
	var label = $("label[for='" + $(this).attr('id') + "']");
	label.css('transform', '');
	$(this).blur()
})

$('#minPlayers').on('input', function() {
	if (parseInt($(this).val()) > parseInt($('#maxPlayers').val())) {
		$('#maxPlayers').val($(this).val())
	}

	if (parseInt($(this).val()) < parseInt($('#minStop').val())) {
		$('#minStop').val($(this).val())
		$('#minStop').trigger('input')
	}
	update_gears()
})

$('#minStop').on('input', function() {
	if (parseInt($(this).val()) > parseInt($('#minPlayers').val())) {
		$('#minPlayers').val($(this).val())
		$('#minPlayers').trigger('input')
	}
	update_gears()
})

$('#maxPlayers').on('input', function() {
	if (parseInt($(this).val()) < parseInt($('#minPlayers').val())) {
		$('#minPlayers').val($(this).val())
	}

	if (parseInt($(this).val()) < parseInt($('#minStop').val())) {
		$('#minStop').val($(this).val())
	}
	update_gears()
})

$('#maxInstances').on('input', function() {
	update_gears()
})

function update_gears() {
	var gears = parseInt($('#maxInstances').val()) * 6
	if (parseInt($('#maxPlayers').val()) - 2 > 0) {
		gears += parseInt($('#maxInstances').val()) * (parseInt($('#maxPlayers').val()) - 2) * 2
	}
	if (parseInt($('#minStop').val()) == 0) {
		gears += 2
	}
	$('#gears').html(gears + '/60')

}

$(document).ready(function() {
	$('.tooltipped').tooltip({
		delay: 50,
	});
	update_gears()
});

function copyToClipboard(element) {
	var $temp = $("<input>");
	$("body").append($temp);
	$temp.val($(element).text()).select();
	document.execCommand("copy");
	$temp.remove();
	Materialize.toast('Copied to clipboard!', 3000, 'rounded')
}

function timeDifference(prev) {
    current = new Date()
    previous = new Date(prev + "z")

    var msPerMinute = 60 * 1000;
    var msPerHour = msPerMinute * 60;
    var msPerDay = msPerHour * 24;
    var msPerMonth = msPerDay * 30;
    var msPerYear = msPerDay * 365;

    var elapsed = (current.getTime() - previous.getTime());

    if (elapsed < msPerMinute) {
         return Math.round(elapsed/1000) + ' seconds';
    }

    else if (elapsed < msPerHour) {
         return Math.round(elapsed/msPerMinute) + ' minutes';
    }

    else if (elapsed < msPerDay ) {
         return Math.round(elapsed/msPerHour ) + ' hours';
    }

    else if (elapsed < msPerMonth) {
        return 'approximately ' + Math.round(elapsed/msPerDay) + ' days';
    }

    else if (elapsed < msPerYear) {
        return 'approximately ' + Math.round(elapsed/msPerMonth) + ' months';
    }

    else {
        return 'approximately ' + Math.round(elapsed/msPerYear ) + ' years';
    }
}