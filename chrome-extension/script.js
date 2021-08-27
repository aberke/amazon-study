

const scrapeOrdersPage = () => {
    let orders = document.getElementsByClassName("order");
    console.log(orders);
    
    let data = JSON.stringify({ todo: 'todo' });

    // send message back to popup script
    chrome.runtime.sendMessage(null, data); 
}



const scrapeProductPage = () => {
    // get the hierarchical category from the breadcrumbs
    let categoriesList = [];
    const breadcrumbsElts = document.querySelector("#wayfinding-breadcrumbs_container ul.a-unordered-list").querySelectorAll("li");
    breadcrumbsElts.forEach( (node) => {
        let a = node.children[0].querySelector("a");
        if (!!a)
            categoriesList = [...categoriesList, a.text.trim()]
    });
    console.log(categoriesList)
    categoriesString = categoriesList.join(" > ");
}

scrapeOrdersPage();
