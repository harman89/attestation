function disclose(e){
   e.parentNode.parentNode.getElementsByClassName("group-content").item(0).classList.toggle("visible");
   // console.log(e);
    //const div = document.getElementById("group-1");
    //div.classList.toggle("visible");
}

function hideParentSelector(){
    const parentSelectorDiv = document.getElementById("parent-selector");
    const gridAndGoalSelectorDiv = document.getElementById("grade-and-goal-selector");
    parentSelectorDiv.classList.toggle("hidden");
    gridAndGoalSelectorDiv.classList.toggle("hidden");
}
//показать/скрыть окно добавления грида
function hideGradeAddBlock(){
    const div = document.getElementById("grade-add-window");
    div.classList.toggle("visible");
}