function add(parent,tag,text,cls){
    const el=document.createElement(tag)
    el.textContent=text
    if(cls){
        el.className=cls
    }
    parent.appendChild(el)
    return el
}
document.addEventListener("DOMContentLoaded",()=>{
    document.querySelectorAll(".alert").forEach(box=>{
        setTimeout(()=>box.remove(),5000)
        const close=box.querySelector(".alert-close")
        if(close){
            close.addEventListener("click",()=>box.remove())
        }
    })
    const burger=document.querySelector(".hamburger")
    const links=document.querySelector(".nav-links")
    if(burger&&links){
        burger.addEventListener("click",()=>links.classList.toggle("show"))
    }
    document.querySelectorAll("[data-confirm]").forEach(el=>{
        el.addEventListener("click",e=>{
            if(!confirm(el.getAttribute("data-confirm"))){
                e.preventDefault()
            }
        })
    })
    const all=document.getElementById("select-all")
    if(all){
        all.addEventListener("change",()=>{
            document.querySelectorAll(".row-cb").forEach(box=>box.checked=all.checked)
        })
    }
    const ngo=document.getElementById("ngo-fields")
    document.querySelectorAll("input[name=role]").forEach(radio=>{
        radio.addEventListener("change",()=>{
            if(ngo){
                ngo.style.display=radio.value=="ngo"?"block":"none"
            }
        })
    })
    const shop=document.getElementById("pharmacy-selector")
    document.querySelectorAll("input[name=fetch_method]").forEach(radio=>{
        radio.addEventListener("change",()=>{
            if(shop){
                shop.style.display=radio.value=="pharmacy"?"block":"none"
            }
        })
    })
    const pass=document.getElementById("password")
    const conf=document.getElementById("confirm_password")
    if(pass&&conf){
        pass.closest("form").addEventListener("submit",e=>{
            if(pass.value!=conf.value){
                e.preventDefault()
                alert("Passwords do not match")
            }
        })
    }
    const btn=document.getElementById("pharmacy-search-btn")
    if(btn){
        btn.addEventListener("click",()=>{
            const pin=document.getElementById("pincode-search").value.trim()
            fetch("/pharmacies/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pincode:pin})})
                .then(res=>res.json())
                .then(list=>{
                    const box=document.getElementById("pharmacy-results")
                    box.replaceChildren()
                    if(!list.length){
                        add(box,"div","No pharmacies found","empty-state")
                        return
                    }
                    list.forEach(p=>{
                        const card=add(box,"div","","card pharmacy-card")
                        add(card,"h4",p.name)
                        add(card,"p",p.address+", "+p.city+" - "+p.pincode)
                        if(p.phone){
                            add(card,"p","Phone: "+p.phone)
                        }
                        add(card,"span","Verified Partner","badge badge-approved")
                    })
                })
        })
    }
})
