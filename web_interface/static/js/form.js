$(document).ready(function() {

	$('#instructionsButton').click(function(){				
		if ($('#instructionsButton').text() == "Show Instructions") {
			$('#instructions').show();
			$('#instructionsButton').html("Hide Instructions");
		}	
		else {
			$('#instructions').hide();
			$('#instructionsButton').html("Show Instructions");
		}	
	});
		

	$('form').on('submit', function(event) {
		$('#result').text('').hide();
		$('#loadingDiv').show();
		window.scrollTo(0,document.body.scrollHeight);
		$('#glamoriseTextarea').attr('disabled', 'disabled');		
		$('#glamoriseJsonConfig').attr('disabled', 'disabled');
		$('#glamoriseJsonConfigInterface').attr('disabled', 'disabled');
		$('#nalirXmlConfig').attr('disabled', 'disabled');
		$('#submitButton').attr('disabled', 'disabled');		
		$.ajax({
			data : {
				nlq : $('#glamoriseTextarea').val(),
				type : $('#hiddenType').val(),
				glamoriseJsonConfig : $('#glamoriseJsonConfig').val(),
				glamoriseJsonConfigInterface : $('#glamoriseJsonConfigInterface').val(),
				nalirXmlConfig : $('#nalirXmlConfig').val()
			},
			type : 'POST',
			url : '/backend'
		})
		.done(function(data) {
			$('#loadingDiv').hide();
			$('#glamoriseTextarea').removeAttr('disabled');
			$('#glamoriseJsonConfig').removeAttr('disabled');
			$('#glamoriseJsonConfigInterface').removeAttr('disabled');
			$('#nalirXmlConfig').removeAttr('disabled');
			$('#submitButton').removeAttr('disabled');
			if (data) {
				$('#result').html(data).show();			
			}			
		});

		event.preventDefault();

	});

});