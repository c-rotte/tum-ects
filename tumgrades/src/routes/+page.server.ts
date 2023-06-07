import { loadSchemaSync } from '@graphql-tools/load';
import { GraphQLFileLoader } from '@graphql-tools/graphql-file-loader';
import { printSchema } from 'graphql';

export async function load() {
	const typeDefs = loadSchemaSync('./../schema/**/*.graphql', {
		loaders: [new GraphQLFileLoader()]
	});

	return {
		gqlTypeDefs: printSchema(typeDefs)
	};
}
