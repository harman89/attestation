function disclose(e){
   e.parentNode.parentNode.getElementsByClassName("group-content").item(0).classList.toggle("visible");
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

//уведомление (пока не применяется)
function showNotification({top = 0, right = 0, className, html}) {

    let notification = document.createElement('div');
    notification.className = "notification";
    if (className) {
        notification.classList.add(className);
    }

    notification.style.top = top + 'px';
    notification.style.right = right + 'px';

    notification.innerHTML = html;
    console.log(document)
    document.body.append(notification);

    setTimeout(() => notification.remove(), 1500);
}
