@router.post("/keyword/{user_id}", response_model=RoleResponse)
async def add_keyword_to_role(
    user_id: int,
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db),
    role_collection: AsyncIOMotorCollection = Depends(get_roles_collection)
):
    # get defining word
    defining_word = db.query(Role).filter(Role.USER_ID == user_id && Role.ROLE_NAME == keyword_data.ROLE_NAME).all()

    # Save to SQL database
    db_role = Role(
        ROLE_NAME=keyword_data.ROLE_NAME,
        ROLE_KEYWORD=keyword_data.ROLE_KEYWORD,
        USER_ID=user_id,
        DEFINING_WORD=defining_word
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

        # Save to MongoDB if needed (optional)
    await role_collection.update_one(
        {"name": keyword_data.ROLE_NAME},
        {"$addToSet": {"positive": keyword_data.ROLE_KEYWORD}},
        upsert=True
    )

    return RoleResponse(
        ROLE_NAME=db_role.ROLE_NAME,
        ROLE_KEYWORD=db_role.ROLE_KEYWORD
    )