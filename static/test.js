class TestModel {
    constructor(data) {
        this.first = data.first;
        this.last = data.last;
        this.id = Number(data.id);
    }

    fullName() {
        return `${this.first} ${this.last}`
    }

    remove() {
        document.getElementById("message").innerText = `removed: ${this.id}`;
    }

    update(first, last) {
        this.first = first;
        this.last = last;
        document.getElementById("message").innerText = `updated: ${this.id}`;
    }
}

class ViewModel {
    constructor(props) {
        this.formElement = document.getElementById("form");
        this.addElement = document.getElementById("add");
        this.messageElement = document.getElementById("message");
        this.deleteAllElement = document.getElementById("deleteAll");
        this.models = [];
        this.loadModels();
        this.setMode('view');
    }

    randomWord(syllable = 6) {
        let newWord = '';
        const vowels = 'aeiou';
        const consonants = 'bcdfghjklmnpqrstvwyz';
        for (let i = 0; i < syllable; i++) {
            let randomPoz = Math.floor(Math.random() * vowels.length);
            newWord += vowels.substring(randomPoz, randomPoz + 1);
            randomPoz = Math.floor(Math.random() * vowels.length);
            newWord += consonants.substring(randomPoz, randomPoz + 1);
        }
        return newWord;
    }

    deleteAll() {
        this.models.forEach(item => item.remove());
        const removedCount = this.models.length;
        this.models = [];
        this.display();
        this.messageElement.innerText = `removed: ${removedCount}`
    }

    setMode(value) {
        if (this.mode !== value) {
            this.mode = value;
            this.display();
        }
    }

    add() {
        this.setMode('add');
    }

    cancel() {
        this.setMode('view');
    }

    submit() {
        const id = this.models.reduce((accum, item) => Math.max(accum, item.id), 0) + 1;
        const new_first = document.getElementById("new_first").value;
        const new_last = document.getElementById("new_last").value;
        if (new_first.length < 1) {
            this.messageElement.innerText = "first name required";
            return;
        }
        if (new_last.length < 1) {
            this.messageElement.innerText = "last name required";
            return;
        }
        this.models.push(new TestModel({first: new_first, last: new_last, id: id}));
        this.messageElement.innerText = `added`;
        this.setMode('view');
    }

    loadModels() {
        for (let x = 0; x < 5; x++) {
            this.models.push(new TestModel({first: `F${this.randomWord()}`, last: `L${this.randomWord()}`, id: x}));
        }
    }

    removeModel(index) {
        this.models[index].remove();
        this.models = this.models.filter((item, i) => i !== index);
        this.display();
    }

    updateModel(ctx, index) {
        const first = ctx.parentNode.querySelector("input.first").value;
        const last = ctx.parentNode.querySelector("input.last").value;
        this.models[index].update(first, last);
        this.display();
    }

    display() {
        const div = document.getElementById("content-list");
        div.innerHTML = "";
        this.models.forEach((element, index) => {
            div.innerHTML += `<li id="li-node-${element.id}" data-id="${element.id}"><span>${element.fullName()}</span>
<input class="first" value="${element.first}"> <input class="last" value="${element.last}">
<button class="update" onclick="view.updateModel(this, ${index})">Update</button> 
<button class="remove" onclick="view.removeModel(${index})">Remove</button> 
</li>`;
        });
        if (this.models.length > 0) {
            this.deleteAllElement.classList.remove("hidden");
        } else {
            this.deleteAllElement.classList.add("hidden");
        }
        switch (this.mode) {
            case'add':
                this.formElement.classList.remove("hidden");
                this.addElement.classList.add("hidden");
                break;
            case 'view':
                this.formElement.classList.add("hidden");
                this.addElement.classList.remove("hidden");
                break;
        }
    }
}

let view = null;
document.addEventListener("DOMContentLoaded", () => view = new ViewModel());