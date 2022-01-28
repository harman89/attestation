function disclose(e){
   e.parentNode.parentNode.getElementsByClassName("group-content").item(0).classList.toggle("visible");
   // console.log(e);
    //const div = document.getElementById("group-1");
    //div.classList.toggle("visible");
}

function hideParentSelector(){
    const parentSelectorDiv = document.getElementById("parent-selector");
    const gridAndGoalSelectorDiv = document.getElementById("grid-and-goal-selector");
    parentSelectorDiv.classList.toggle("hidden");
    gridAndGoalSelectorDiv.classList.toggle("hidden");
}

