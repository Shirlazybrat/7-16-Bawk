$(document).ready(function(){
	$('.vote').click(function(e){
		e.preventDefault()
		var vote_id = $(this).attr('post_id')
		if ($(this).hasClass("vote_up")){
			//user clicked on the thumb up 
			var voteType = 1;
			console.log('up')
		}
		else {
			//user clicked on the thumb down
			var voteType = -1;
			console.log('down')
		}
		$.ajax({
			url: "/process_vote",
			type: "post",
			data: {vote_id:vote_id, voteType:voteType},
			success: function(result){
				if (result.message == 'voteChanged'){
					// the users vote was updated by python, updat in field
					($("div[up-down-id='" + vote_id + "']").html(result.vote_total))
				}
				else if ( result.message == 'alreadyVoted'){
					$("div[up-down-id='" + vote_id + "']").html("you already voted for this buzz!")
				}
				console.log(result)
			},
			error: function(error){
				console.log("not working")
			}
		});
	});
});