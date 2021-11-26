import requests, json, jwt, sys

def _test(ok_val, text, err_msg=None):
    if ok_val:
        print(text + ":\033[1;32m OK \033[0m")
    elif err_msg:
        print(text + ":\033[1;31m ERROR [{err}]\033[0m".format(err=err_msg))
        sys.exit()
    else:
        print(text + ":\033[1;31m ERROR\033[0m")
        sys.exit()
		

def create_user(url):
	nombre = input("Nombre: ")
	apellido = input("Apellido: ")
	email = input("Correo electronico: ")

	url_create_user = url + "/challenge/create_user"

	data = json.dumps({
	"nombre": nombre,
	"apellido": apellido,
	"email": email
	})

	headers = {
	'Content-Type': 'application/json'
	}

	r_create_user = requests.post(url_create_user, headers=headers, data=data)
	return r_create_user

def auth_mailer(url, doc, device):
	url_auth_mailer = url + "/cd/auth_mailer"

	data = json.dumps({
	"documento": doc,
	"device":device
	})

	headers = {
	'Content-Type': 'application/json'
	}

	r_auth_mailer = requests.post(url_auth_mailer, headers=headers, data=data)
	return r_auth_mailer

def autenticacion(url, payload_decoded):
	url_autenticacion = url + "/cd/autenticacion"

	params = {
		"doc":payload_decoded['doc'],
		"date_created":payload_decoded['date_created'],
		"sp":payload_decoded['sp']
	}

	headers = {'content-type': 'application/json'}

	r_autenticacion = requests.get(url_autenticacion, params = params, headers = headers)
	return r_autenticacion

def perfilsocio(url, payload_decoded):
	url_perfilsocio = url + "/cd/autenticacion"

	payload_json = json.dumps(payload_decoded)
	headers = {"Authorization": payload_json, 'content-type': 'application/json'}

	r_perfilsocio = requests.get(url_perfilsocio, headers = headers)
	return r_perfilsocio

def checkout():
	url_checkout = "https://checkout.sportclub.com.ar/paso2/"

	r_checkout_ypf = requests.get(url_checkout + 'ypf')
	r_checkout_total_mensual = requests.get(url_checkout + 'total-mensual')

	return r_checkout_ypf,r_checkout_total_mensual

def procesos_nuevos_clientes():
	url_procesos = 'https://procesos.apisportclub.xyz/nuevos_clientes'
	r_procesos = requests.get(url_procesos)
	return r_procesos


def main():
	url = "https://apisportclub.xyz"

	r_create_user = create_user(url)
	user_data = r_create_user.json()
	_test(r_create_user.ok, "Aplicación credencial digital", r_create_user.reason)

	device = "chrome"
	r_auth_mailer = auth_mailer(url, user_data['documento'], device)
	token = r_auth_mailer.json()['token']
	_test(r_auth_mailer.ok, "Auth Mailer", r_auth_mailer.reason)

	payload_decoded = jwt.decode(token, options={"verify_signature": False})

	_test(payload_decoded['doc'] == user_data['documento'], "Documento")
	_test(payload_decoded['id'] == user_data['_id'], "ID")
	_test(payload_decoded['device'] == device, "Device")

	r_autenticacion = autenticacion(url, payload_decoded)
	_test(r_autenticacion.ok, "Autenticacion", r_autenticacion.reason)

	r_perfilsocio = perfilsocio(url, payload_decoded)
	_test(r_perfilsocio.ok, "Perfil socio", r_perfilsocio.reason)

	r_ypf,r_total_mensual = checkout()
	_test(r_ypf.ok, "Checkout YPF", r_ypf.reason)
	_test(r_total_mensual.ok, "Checkout total-mensual", r_total_mensual.reason)

	r_procesos = procesos_nuevos_clientes()
	_test(r_procesos.ok, "Procesos back, nuevos clientes", r_procesos.reason)


main()