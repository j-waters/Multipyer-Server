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

$(document).ready(function() {
	Materialize.updateTextFields();
	$('.modal').modal({
		endingTop: '50%'
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

$("#settingsForm").submit(function(event) {

	/* stop form from submitting normally */
	event.preventDefault();

	/* get some values from elements on the page: */
	var $form = $(this)

	/* Send the data using post */
	var posting = $.post("{{ url_for('server_settings') }}", {
		id: { %
			if selected is not none %
		} {
			{
				selected.id
			}
		} { %
			else %
		}
		"" { % endif %
		},
		min_clients: $form.find('input[name="min_clients"]').val(),
		max_clients: $form.find('input[name="max_clients"]').val(),
		min_stop: $form.find('input[name="min_stop"]').val(),
		max_instances: $form.find('input[name="max_instances"]').val(),
		name: $form.find('input[name="servername"]').val()
	});

	/* Put the results in a div */
	posting.done(function(data) {
		Materialize.toast('Settings Applied', 3000, 'rounded')
		refresh_servers()
	});
});

function refresh_servers() {
	$.get("{{ url_for('server_data', target='all') }}", function(data) {
		data = JSON.parse(data)
		for (var key in data) {
			dat = data[key]
			if (dat['state'] == 'good') {
				$('#S' + dat['id']).children('img').attr('src', '{{ url_for('
					static ', filename='
					images / working.png ')}}')
			}
			if (dat['state'] == 'warning') {
				$('#S' + dat['id']).children('img').attr('src', '{{ url_for('
					static ', filename='
					images / warning.png ')}}')
			}
			if (dat['state'] == 'error') {
				$('#S' + dat['id']).children('img').attr('src', '{{ url_for('
					static ', filename='
					images / error.png ')}}')
			}
			$('#S' + dat['id']).children('p').children('#sGears').html(dat['gears'])
			$('#S' + dat['id']).children('p').children('#sInstances').html(dat['instances'])
		}
	})
}