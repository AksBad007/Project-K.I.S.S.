document.querySelector("#list-btn").addEventListener('click',()=>{
    let delForm = document.querySelector("#delForm")
    const div = document.createElement('div'); const i =  document.createElement('input'); const para = document.createElement('p')
    i.type = 'checkbox'; i.name = 'check'; i.id = 'list-check'; i.checked=delForm.submit()
    para.id = "list-p"; para.innerText = document.querySelector('#newItem').value
    div.className = 'item'; div.append(i); div.append(para)
    document.querySelector("#listParent").insertBefore(div, document.querySelector("#listParent").children[0])
    delForm.append(div)
})
fetch('/json').then(res => {
    return res.json()
}).then(data => {
    let items = data.items[0]
    for(let i=0;i<items.listItems.length;i++){
        let delForm = document.querySelector("#delForm")
        const div = document.createElement('div'); const something =  document.createElement('input'); const para = document.createElement('p')
        something.type = 'checkbox'; something.name = 'check'; something.id = `list-check${i}`; something.value=items.listItems[i].id            
        para.id = "list-p"; para.innerText = items.listItems[i].name
        div.className = 'item'; div.id=`item${i}`; div.append(something); div.append(para)
        document.querySelector("#listParent").insertBefore(div, document.querySelector("#listParent").children[0])
        delForm.append(div)
    }
}).catch(e => alert(e)).then(()=>{
    let itemID = document.querySelectorAll('.item')
    for(let i=0; i<itemID.length; i++){
        let aVar = document.querySelector(`#list-check${i}`)
        aVar.addEventListener('click',()=>{
            let pranjal = parseInt(aVar.value)
            let formData = new FormData()
            formData.append('check',pranjal)
            fetch('/del',{
                method:"POST",
                body:formData
            })
        })
    }
})