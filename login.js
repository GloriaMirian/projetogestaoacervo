const form = document.querySelector("form");

form.addEventListener("submit", function (event) {
    event.preventDefault();

    const usuario = document.getElementById("usuario").value.trim();
    const senha = document.getElementById("senha").value;

    // Usuário e senha provisórios
    const usuarioCorreto = "admin";
    const senhaCorreta = "123456";

    if (usuario === usuarioCorreto && senha === senhaCorreta) {

        // Salva o usuário caso "Lembrar de mim" esteja marcado
        const lembrar = document.getElementById("lembrar").checked;

        if (lembrar) {
            localStorage.setItem("usuario", usuario);
        } else {
            localStorage.removeItem("usuario");
        }

        // Entra no sistema
        window.location.href = "dashboard.html";

    } else {

        alert("Usuário ou senha incorretos.");
    }
});
