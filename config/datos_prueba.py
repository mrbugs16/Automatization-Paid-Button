"""
Datos de prueba y mensajes esperados del Botón de Pago.
Los mensajes son los textos exactos que muestra la página (tomados de su código).
"""

# ==============================================
# PASO 1 - CONTACTO
# ==============================================
CONTACTO_VALIDO = {"telefono": "5540076333", "correo": "santiago.tapia@memphis.mx"}
CORREO_SIN_ARROBA = "contribuyentecorreo.com"
CORREO_CON_ESPACIOS = "  santiago.tapia@memphis.mx  "
CORREOS_INVALIDOS = [
    "contribuyentecorreo.com",       # sin arroba
    "santiago.tapia@",               # sin dominio
    "santiago.tapia@memphis",        # sin extensión (.mx, .com)
    "santiago..tapia@memphis.mx",    # doble punto
    "santiago tapia@memphis.mx",     # espacio interno
    "@memphis.mx",                   # sin usuario
    "santiago.tapia@memphis.x",      # extensión de 1 letra
]
TELEFONO_INCOMPLETO = "12345"
TELEFONO_CON_LETRAS = "abc123"
TELEFONO_SOLO_LETRAS = "abcdefghij"
TELEFONO_LARGO = "55400763331234"  # 14 dígitos (máximo permitido: 13)

# ==============================================
# PASO 2 - DIRECCIÓN
# ==============================================
DIRECCION_VALIDA = {"calle": "Reforma 245", "cp": "16200", "ciudad": "Cholula", "pais": "MEX", "estado": "PUE"}
CP_INCOMPLETO = "2000"
CP_CORTO = "123"
CALLE_CON_SIMBOLOS = "Av. Juárez #12"
CIUDAD_CON_ACENTOS = "Tehuacán"

# ==============================================
# PASO 3 - TARJETA
# ==============================================
NOMBRE_COMPUESTO = "Juan Carlos"
APELLIDO_COMPUESTO = "Pérez López"      # es el ejemplo que muestra el propio campo
NOMBRE_CON_NUMEROS = "Juan2"
NUMERO_TARJETA_INVALIDO = "4111111111111112"   # 16 dígitos, dígito verificador incorrecto
NUMERO_TARJETA_CORTO = "411111111111"          # 12 dígitos
VIGENCIA_VENCIDA = "0120"
VIGENCIA_MES_INVALIDO = "1329"
VIGENCIA_INCOMPLETA = "052"
CVV_INCOMPLETO = "12"

# ==============================================
# MENSAJES ESPERADOS
# ==============================================
MSG_REQUERIDO = "Este campo es requerido"
MSG_CORREO_INVALIDO = "El campo email debe tener un formato de correo."
MSG_TELEFONO = "El número de teléfono debe tener mínimo 10 dígitos"
MSG_CP = "Debe ser un código postal válido."
MSG_NATIVO_SELECCIONA = "Please select an item in the list."  # aviso del navegador en el select de Estado
MSG_SOLO_LETRAS_NUMEROS = "Sólo se permiten letras y números con espacios"
MSG_NOMBRE = "Sólo se permiten letras con acentos"
MSG_TARJETA_LONGITUD = "La tarjeta debe tener 15 o 16 dígitos"
MSG_VIGENCIA_LONGITUD = "Debe tener 4 dígitos"
MSG_VIGENCIA_INVALIDA = "Fecha de vencimiento inválida"
MSG_CVV = "El CVV debe tener 3 dígitos"
MSG_LINK_INVALIDO = "Link de pago no válido"
MSG_TOAST_ERROR = "Ha ocurrido un error al procesar el pago."
TITULO_APROBADA = "Transacción aprobada"
TITULO_RECHAZADA = "Transacción rechazada"
