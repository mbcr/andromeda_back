### Script to extract an array of dictionaries from XLSX file
### <-----It remains to convert the data of interest (columns) into a dictionary to be passed as an argument.----->

def extractExcelToDictionaryArray(fileData,withHeaders=False):
    import openpyxl
    import os

    #Set behaviour
    if withHeaders:
        initialRow=0
    else:
        initialRow=1

    #Access file
    dirName = fileData['dirName']
    fileName = fileData['fileName']
    workSheetName = fileData['workSheetName']
    numberOfRows = fileData['numberOfRows']
    
    os.chdir(dirName)
    wb=openpyxl.load_workbook(fileName,data_only=True)
    wsDatabase = wb[workSheetName]
    database = tuple(wsDatabase.rows)
    print(f"File {fileName} read and database defined with {len(database)} rows.")


    ##Load data
    #Define location columns for Data of interest
    coluna_nome = 0
    coluna_codigo = 1
    coluna_razaoSocial = 2
    #coluna_data_cadastro = 3
    coluna_cnpj = 4
    coluna_status_cadastro_clinica = 20 #!
    coluna_cep = 6
    coluna_endereco_logradouro = 7
    coluna_endereco_numero = 8
    coluna_endereco_bairro = 9
    coluna_endereco_complemento = 10
    coluna_endereco_municipio = 19 #!
    coluna_endereco_uf = 12 #!
    coluna_latitude = 17
    coluna_longitude = 18
    #coluna_telefone_regiao = 13 #!!!
    coluna_telefone_numero = 13 #!!!
    coluna_email = 14
    coluna_tipo_agendamento = 15 #!
    #coluna_numeroGeoLocalizacoes = 16


    #Extract data and append each row's data into the result array
    result = []
    for row in range (initialRow,numberOfRows):
        nome = database[row][coluna_nome].value
        codigo = database[row][coluna_codigo].value
        razaoSocial = database[row][coluna_razaoSocial].value
        #data_cadastro = database[row][coluna_data_cadastro].value
        cnpj = database[row][coluna_cnpj].value
        status_cadastro_clinica = database[row][coluna_status_cadastro_clinica].value
        cep = database[row][coluna_cep].value
        endereco_logradouro = database[row][coluna_endereco_logradouro].value
        endereco_numero = database[row][coluna_endereco_numero].value
        endereco_bairro = database[row][coluna_endereco_bairro].value
        endereco_complemento = database[row][coluna_endereco_complemento].value
        endereco_municipio = database[row][coluna_endereco_municipio].value
        endereco_uf = database[row][coluna_endereco_uf].value
        # Separar telefone em dois campos
        telefone_numero = database[row][coluna_telefone_numero].value
        #telefone_regiao = database[linha][coluna_telefone_regiao].value
        #telefone_numero = database[linha][coluna_telefone_numero].value
        email = database[row][coluna_email].value
        tipo_agendamento = database[row][coluna_tipo_agendamento].value
        #numeroGeoLocalizacoes = database[row][coluna_numeroGeoLocalizacoes].value
        latitude = database[row][coluna_latitude].value
        longitude = database[row][coluna_longitude].value
        

        newItem = {
            'nome': nome,
            'codigo': codigo,
            'razaoSocial': razaoSocial,
            #'data_cadastro': data_cadastro,
            'cnpj': cnpj,
            'status_cadastro_clinica': status_cadastro_clinica,
            'cep': cep,
            'endereco_logradouro': endereco_logradouro,
            'endereco_numero': endereco_numero,
            'endereco_bairro': endereco_bairro,
            'endereco_complemento': endereco_complemento,
            'endereco_municipio': endereco_municipio,
            'endereco_uf': endereco_uf,
            'telefone_numero': telefone_numero,
            'email': email,
            'tipo_agendamento': tipo_agendamento,
            #'numeroGeoLocalizacoes': numeroGeoLocalizacoes,
            'latitude': latitude,
            'longitude': longitude,
            
            }

        result.append(newItem)

    print(f"Database successfully transcribed to array")

    return result

##For self-contained usage:
#Define target file and number of rows to extract
# dirName = 'C:\\Users\\marco\\Desktop\\Trabalhos\\Coding\\Public API Interaction'
# fileName = "GeoClinics5.xlsx"
# workSheetName = 'DB Clinicas'
# numberOfRows= 915

# file = {
#     'dirName': dirName,
#     'fileName': fileName,
#     'workSheetName': workSheetName,
#     'numberOfRows': numberOfRows
#     }

# clinicas = extractExcelToDictionaryArray(file,withHeaders=False)
