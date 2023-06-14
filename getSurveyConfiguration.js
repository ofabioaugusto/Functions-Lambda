const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB();

exports.handler = async(event) => {
    const response = {
        statusCode: 200
    };

    var params = {
        TableName: process.env.TABLE, // a tabela configurada na variável de ambiente desta função
        Key: {
            'surveyId': { S: event.Details.Parameters.surveyId } // extraindo o surveyId do atributo de contato "surveyId"
        }
    };

    try {
        let res = await ddb.getItem(params).promise(); // leia a tabela do DynamoDB

        if (res.Item) {
            response.message = 'OK';

            let size = 0; // armazenando o "size" da pesquisa (ou seja, o número de perguntas)

            // extraia todas as propriedades da entrada retornada e atualize o tamanho da pesquisa

            Object.keys(res.Item).forEach(k => {
                response[k] = res.Item[k].S;

                size = k.startsWith('question') ? size + 1 : size;
            });

            response.surveySize = size;
        } else {
            response.message = `Não foi possível encontrar configuração para pesquisa com id [${event.Details.Parameters.surveyId}]`;
        }

    } catch (err) {
        console.log(err);
    }

    return response; // por fim, retornamos a resposta ao Amazon Connect

};