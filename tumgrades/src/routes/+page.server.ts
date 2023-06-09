import { PrismaClient } from '@prisma/client';

export async function load() {
	const prisma = new PrismaClient();
	const degrees = await prisma.degree.findMany();
	return {
		degrees: degrees
	};
}
