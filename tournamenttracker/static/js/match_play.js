/* ------------------------------------------------------------------------------------------------------------------ */
/* PLAY GAME - Count up timer */
/* ------------------------------------------------------------------------------------------------------------------ */

// Count up timer for game duration once the game has been started
function countUpFromTime(start_time, element_id) {
  start = moment.utc(start_time);
  now = moment.utc();
  diff = now - start;

  var hours = Math.floor(diff / (60 * 60 * 1000));
  diff = diff - (hours * (60 * 60 * 1000));
  var minutes = Math.floor(diff / (60 * 1000));
  diff = diff - (minutes * (60 * 1000));
  var seconds = Math.floor(diff / (1000));

  if (hours > 0) {
    var time = addLeadingZero(hours) + ':' + addLeadingZero(minutes) + ':' + addLeadingZero(seconds);
  } else {
    var time = addLeadingZero(minutes) + ':' + addLeadingZero(seconds);
  }

  var element = document.getElementById(element_id);
  element.innerHTML = time;

  clearTimeout(countUpFromTime.interval);
  countUpFromTime.interval = setTimeout(function(){ countUpFromTime(start_time, element_id); }, 1000);
}

function addLeadingZero(n) {
	n = n.toString();
  if (n.length == 1) {
  	return ('0' + n.slice(-2))
  }
  return n
}

/* ------------------------------------------------------------------------------------------------------------------ */
/* PLAY GAME - Drop and drag grid */
/* ------------------------------------------------------------------------------------------------------------------ */

function matchDropAndDrag() {
  const empties = document.querySelectorAll('.empty');
  var draggedItem = null;

  // Loop through empty boxes and add listeners
  for (const empty of empties) {
    empty.addEventListener('dragstart', dragStart);
    empty.addEventListener('dragend', dragEnd);
    empty.addEventListener('dragover', dragOver);
    empty.addEventListener('dragenter', dragEnter);
    empty.addEventListener('dragleave', dragLeave);
    empty.addEventListener('drop', dragDrop);
  }

    // Drag Functions
    function dragStart(e) {
      draggedItem=this;
      this.className = 'empty hold';
      e.dataTransfer.setData('text', '');
    }

    function dragEnd() {
      this.className = 'empty';  // required to turn the class from invisible back to fill once dragging is complete
    }

    function dragOver(e) {
      e.preventDefault();
      if (this.className == 'empty') {
        this.className += ' hovered';
      }
    }

    function dragEnter(e) {
      e.preventDefault();
      this.className += ' hovered';
    }

    function dragLeave() {
      this.className = 'empty';
    }

    function dragDrop(e) {
      if (e.stopPropagation) {
        e.stopPropagation(); // stops some browsers from redirecting.
      }
      origPos = draggedItem.parentElement.id
      newPos = this.parentElement.id;

      if (origPos != newPos) {  // don't swap if dropped on the same position
          var newPosDataCopy = this.innerHTML;
          this.innerHTML = draggedItem.innerHTML;
          draggedItem.innerHTML = newPosDataCopy;
          this.className = "empty";
          updateSelectOption('Manual', 'balance_mode');
          updateGameBalance();
          return true;
      }
      return false;
    }
}


/* ------------------------------------------------------------------------------------------------------------------ */
/* PLAY GAME - Match player grid */
/* ------------------------------------------------------------------------------------------------------------------ */

function matchPlayerGrid(playerPositions) {
    console.log('matchPlayerGrid()', playerPositions);

    if (!playerPositions.balanced) {
        console.log('Match is not balanced. No update.');
        return false;
    }

    for (var playerId of Object.keys(playerPositions.players)) {
        let team = playerPositions.players[playerId].team;
        let position = playerPositions.players[playerId].position;
        let won = playerPositions.players[playerId].won;
        let mvp = playerPositions.players[playerId].mvp;

        origPlayerDiv = findChildNodeListByClass('position-' + position, 'empty')[0];
        newPlayerDiv = document.getElementById('player-' + playerId).parentElement;

        if (newPlayerDiv) {
            if (origPlayerDiv != newPlayerDiv) {
                var temp = origPlayerDiv.innerHTML;
                origPlayerDiv.innerHTML = newPlayerDiv.innerHTML;
                newPlayerDiv.innerHTML = temp;
            }
            if (won) {
                // Add won css to player position
                origPlayerDiv.classList.add("won");
            }
            if (mvp) {
                // Add mvp css to player
                console.log(origPlayerDiv);
                origPlayerDiv.classList.add("mvp");
            }
        }
    }
    updateGameBalance();
}


/* ------------------------------------------------------------------------------------------------------------------ */
/* PLAY GAME - Start / End */
/* ------------------------------------------------------------------------------------------------------------------ */

function startMatch(url) {
    json = matchStartData();
    console.log(url, json);
    postData(url, json);
}


function endMatch(url) {
    json = matchEndData();
    console.log(url, json);
    postData(url, json);
}


function matchStartData() {
    data = {};

    data['balance_mode_id'] = getSelectOptionValue('balance_mode');
    data['players'] = getCurrentPlayerPositions();

    return data;
}


function matchEndData() {
    data = {};

    data['winning_team'] = getSelectOptionValue('winning_team');
    data['mvp'] = getSelectOptionValue('mvp');

    return data;
}

/* ------------------------------------------------------------------------------------------------------------------ */
/* PLAY GAME - Balancing */
/* ------------------------------------------------------------------------------------------------------------------ */




// Function that keeps track of the balance state and updated when changes occur
function balanceGameStart(balanceModeDict, selectElementId) {
    console.log(balanceModeDict);
    selectElem = document.getElementById(selectElementId);  // get the select element from the document
    selectElem.addEventListener('change', balanceUpdate.bind(event, balanceModeDict, selectElementId));  // add a listener for when the select mode changes
    balanceUpdate(balanceModeDict, selectElementId);
}


function balanceUpdate (balanceModeDict, selectElementId) {
        balance_mode_id = getSelectOptionValue(selectElementId);  // get the balance_mode_id from the current selection
        console.log(balance_mode_id, balanceModeDict[balance_mode_id]);
        balanceMatch(balanceModeDict[balance_mode_id]);  // balance the match
        updateGameBalance();
    }


// Balance the player_id's in the order of the array passed to the function
function balanceMatch(balance_array) {

  if (balance_array == null) {
    return false;
  }

  balance_array.forEach(function (player_id, index) {  // cycle through the balance list
  	if (player_id == null) {
  	    return false;
  	}

  	origPlayerDiv = findChildNodeListByClass('position-' + (index + 1).toString(), 'empty')[0];
    newPlayerDiv = document.getElementById('player-' + player_id.toString()).parentElement;
    if (newPlayerDiv) {  // if the player div is found
        if (origPlayerDiv != newPlayerDiv) {
          temp = origPlayerDiv.innerHTML;
          origPlayerDiv.innerHTML = newPlayerDiv.innerHTML;
          newPlayerDiv.innerHTML = temp;
        }
    }
  })
  return true;
}


function getCurrentPlayerPositions() {
    playerPositions = {};
    playerElems = document.querySelectorAll('.player-info');

    for (const playerElem of playerElems) {
        var player_id = getNumberAfterDash(playerElem.id);
        var position = getNumberAfterDash(playerElem.parentNode.parentNode.id);
        var team = getNumberAfterDash(playerElem.parentNode.parentNode.parentNode.id);
        var rating = parseInt(playerElem.attributes.rating.value);
        playerPositions[player_id] = {player_id: player_id, team: team, position: position, rating: rating};
    }
    return playerPositions;
}


// Update the percentage rating chance for a team to win
function updateGameBalance() {
    teams = document.getElementsByClassName('team').length;
    playerStats = getCurrentPlayerPositions();
    var teamScore = {};
    for (var i=1; i <= teams; i++) { teamScore[i] = 0; }  // initialise teamScore object with a score of 0
    teamScore['total'] = 0;

    for (var x in playerStats) {
        teamScore[playerStats[x].team] += playerStats[x].rating;
        teamScore['total'] += playerStats[x].rating;
    }

    for (var i=1; i <= teams; i++) {
        teamElem = document.getElementById('balance-team-' + i);
        var percentage = ((teamScore[i] / teamScore.total) * 100).toFixed(1);
        if (percentage >= 0 && percentage <= 100) {
            teamElem.innerHTML = percentage;
        } else {
            teamElem.innerHTML = 0.0;
        }
     }
}


/* ------------------------------------------------------------------------------------------------------------------ */
/* GENERIC FUNCTIONS */
/* ------------------------------------------------------------------------------------------------------------------ */

function getNumberAfterDash(str) {
  return parseInt(str.split("-")[1]);
}


function getSelectOptionId(selectElementId) {
	selectElem = document.getElementById(selectElementId);
  if (selectElem) {
  	return selectElem.selectedIndex;
  }
  return false;
}

function getSelectOptionValue(selectElementId) {
selectElem = document.getElementById(selectElementId);
  if (selectElem) {
  	return selectElem.options[selectElem.selectedIndex].value;
  }
  return false;
}



function getSelectOptionLabel(selectElementId) {
selectElem = document.getElementById(selectElementId);
  if (selectElem) {
  	return selectElem.options[selectElem.selectedIndex].label;
  }
  return false;
}


function updateSelectOption(optionString, selectElementId) {
	var sel = document.getElementById(selectElementId);
  var opts = sel.options;
  for (var opt, j = 0; opt = opts[j]; j++) {
    if (opt.label == optionString) {
      sel.selectedIndex = j;
      break;
    }
  }
}


function findChildNodeListById(parentId, childIdName) {
	var foundList = [];
    parentNode = document.getElementById(parentId);
    if (parentNode)
    {
        result = findChildNodeById(parentNode, childIdName, foundList);
    }
    return foundList;
}


function findChildNodeListByClass(parentId, childClassName) {
	var foundList = [];
    parentNode = document.getElementById(parentId);
    if (parentNode)
    {
        result = findChildNodeByClass(parentNode, childClassName, foundList);
    }
    return foundList;
}


function findChildNodeByClass(nodeParent, childClassName, foundList) {
  if (nodeParent.childNodes.length > 0) {
  	nodeParent.childNodes.forEach(function (child, index) {

      if (child.className == childClassName) {
      	foundList.push(child);
         return true;
      }
      findChildNodeByClass(child, childClassName, foundList);
  	});
	}
}


function findChildNodeById(parentNode, childId, foundList) {
    if (parentNode.childNodes.length > 0) {
  	    parentNode.childNodes.forEach(function (child, index) {

         if (child.id == childId) {
           console.log(child);
            foundList.push(child);
            return child;
         }

        findChildNodeById(child, childId, foundList);
  	    });
	}
}


function postData(url, json) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this);
            document.location.pathname = this.responseText;
            console.log(this);
        }
    }
    xhr.send(JSON.stringify(json));
}


function getData(url) {
    var xhr = new XMLHttpRequest();
    // we defined the xhr

    xhr.onreadystatechange = function () {
        if (this.readyState != 4) return;

        if (this.status == 200) {
            var data = JSON.parse(this.responseText);

            // we get the returned data
        }

        // end of state change: it can be after some time (async)
    };

    xhr.open('GET', url, true);
    xhr.send();
}