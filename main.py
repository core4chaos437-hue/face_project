from register import (
    register_via_webcam,
    register_via_photo,
    list_all_people,
    delete_person
)
from recognize import recognize_from_photo, recognize_live
from database_manager import (
    print_record,
    print_all_records,
    show_original_photo,
    show_all_sightings
)
import os

def main():
    while True:
        print("\n" + "="*40)
        print("    FACE RECOGNITION SYSTEM")
        print("="*40)
        print("  REGISTER")
        print("  1. Add person via webcam")
        print("  2. Add person via photo")
        print("")
        print("  RECOGNISE")
        print("  3. Test a photo (disguise test)")
        print("  4. Live webcam recognition")
        print("")
        print("  RECORDS")
        print("  5. View all records")
        print("  6. View one person's full history")
        print("  7. View original photo of person")
        print("  8. View all sighting photos")
        print("")
        print("  9. Delete a person")
        print("  0. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            if name:
                register_via_webcam(name)

        elif choice == "2":
            name = input("Name: ").strip()
            path = input("Photo path: ").strip()
            if os.path.exists(path):
                register_via_photo(name, path)
            else:
                print("❌ File not found")

        elif choice == "3":
            path = input("Test photo path: ").strip()
            if os.path.exists(path):
                recognize_from_photo(path)
            else:
                print("❌ File not found")

        elif choice == "4":
            recognize_live()

        elif choice == "5":
            print_all_records()

        elif choice == "6":
            name = input("Name: ").strip()
            print_record(name)

        elif choice == "7":
            name = input("Name: ").strip()
            show_original_photo(name)

        elif choice == "8":
            name = input("Name: ").strip()
            show_all_sightings(name)

        elif choice == "9":
            name = input("Name to delete: ").strip()
            delete_person(name)

        elif choice == "0":
            print("👋 Bye!")
            break

if __name__ == "__main__":
    main()