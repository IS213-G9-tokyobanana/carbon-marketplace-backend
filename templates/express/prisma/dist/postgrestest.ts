import { PrismaClient } from "@prisma/client"

const prisma = new PrismaClient()

async function main() {
	// Prisma Client queries go here
	const newUser = await prisma.user.create({
		data: {
			name: "Ayaka",
			email: "Ayaka@smu.edu.sg",
			projects: {
				create: {
					title: "Save the World",
				},
			},
		},
	})
	console.log("Created new user: ", newUser)

	const allUsers = await prisma.user.findMany({
		include: { projects: true },
	})
	console.log("All users: ")
	console.dir(allUsers, { depth: null })
}

main()
	.catch((e) => console.error(e))
	.finally(async () => await prisma.$disconnect())
