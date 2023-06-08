import { PrismaClient } from '@prisma/client';

export async function load() {
	const prisma = new PrismaClient();
	const modules = await prisma.module.findMany();
	return {
		modules: modules
	};
}
